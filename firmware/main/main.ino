#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include "config.h"

// ── Globals ──────────────────────────────────────────────────────────────────
DHT dht(PIN_DHT, DHT22);
WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

bool  pumpRunning      = false;
unsigned long pumpStartMs  = 0;
unsigned long lastSensorMs = 0;

// ── WiFi ─────────────────────────────────────────────────────────────────────
void connectWiFi() {
  Serial.printf("Connecting to WiFi: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nWiFi connected. IP: %s\n", WiFi.localIP().toString().c_str());
}

// ── MQTT ─────────────────────────────────────────────────────────────────────
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  Serial.printf("MQTT [%s]: %s\n", topic, msg.c_str());

  if (String(topic) == TOPIC_PUMP_CONTROL) {
    StaticJsonDocument<128> doc;
    if (deserializeJson(doc, msg) == DeserializationError::Ok) {
      String action = doc["action"] | "";
      if (action == "on")  startPump();
      if (action == "off") stopPump();
    }
  }
}

void connectMqtt() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqtt.connect(MQTT_CLIENT_ID)) {
      Serial.println(" connected.");
      mqtt.subscribe(TOPIC_PUMP_CONTROL);
    } else {
      Serial.printf(" failed (rc=%d). Retry in 5s\n", mqtt.state());
      delay(5000);
    }
  }
}

// ── Pump ─────────────────────────────────────────────────────────────────────
void startPump() {
  if (pumpRunning) return;
  digitalWrite(PIN_PUMP_RELAY, LOW);   // LOW activates most relay modules
  pumpRunning = true;
  pumpStartMs = millis();
  Serial.println("Pump ON");
  mqtt.publish(TOPIC_PUMP_STATUS, "{\"status\":\"on\"}");
}

void stopPump() {
  if (!pumpRunning) return;
  digitalWrite(PIN_PUMP_RELAY, HIGH);
  pumpRunning = false;
  Serial.println("Pump OFF");
  mqtt.publish(TOPIC_PUMP_STATUS, "{\"status\":\"off\"}");
}

// ── Sensors ───────────────────────────────────────────────────────────────────
int readSoilMoisture() {
  // Average 5 readings to reduce noise
  long sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += analogRead(PIN_SOIL_MOISTURE);
    delay(10);
  }
  return sum / 5;
}

float soilMoisturePercent(int raw) {
  // Capacitive sensor: ~3300 = dry air, ~1200 = fully submerged
  // Map to 0-100%
  return constrain(map(raw, 3300, 1200, 0, 100), 0, 100);
}

void publishSensors() {
  int   soilRaw  = readSoilMoisture();
  float moisture = soilMoisturePercent(soilRaw);
  float temp     = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temp) || isnan(humidity)) {
    Serial.println("DHT read failed");
    return;
  }

  StaticJsonDocument<256> doc;
  doc["device_id"]     = MQTT_CLIENT_ID;
  doc["soil_moisture"] = moisture;
  doc["temperature"]   = temp;
  doc["humidity"]      = humidity;
  doc["pump_on"]       = pumpRunning;

  char buf[256];
  serializeJson(doc, buf);
  mqtt.publish(TOPIC_SENSORS, buf);
  Serial.printf("Published: %s\n", buf);

  // Auto-watering logic: trigger if soil too dry
  if (soilRaw > MOISTURE_DRY_THRESHOLD && !pumpRunning) {
    Serial.println("Soil dry — auto-watering");
    startPump();
  }
  if (soilRaw < MOISTURE_WET_THRESHOLD && pumpRunning) {
    Serial.println("Soil wet — stopping pump");
    stopPump();
  }
}

// ── Setup & Loop ──────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  pinMode(PIN_PUMP_RELAY, OUTPUT);
  digitalWrite(PIN_PUMP_RELAY, HIGH);  // Relay off by default

  dht.begin();
  connectWiFi();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
}

void loop() {
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  // Safety: auto-stop pump after max duration
  if (pumpRunning && (millis() - pumpStartMs >= PUMP_MAX_DURATION_MS)) {
    Serial.println("Pump max duration reached — stopping");
    stopPump();
  }

  // Publish sensor readings on interval
  if (millis() - lastSensorMs >= SENSOR_INTERVAL_MS) {
    lastSensorMs = millis();
    publishSensors();
  }
}
