#pragma once

// WiFi
#define WIFI_SSID       "YOUR_WIFI_SSID"
#define WIFI_PASSWORD   "YOUR_WIFI_PASSWORD"

// MQTT Broker
#define MQTT_HOST       "192.168.1.100"  // IP of your backend server
#define MQTT_PORT       1883
#define MQTT_CLIENT_ID  "esp32-plant-01"

// MQTT Topics
#define TOPIC_SENSORS       "plant/sensors"
#define TOPIC_PUMP_STATUS   "plant/pump/status"
#define TOPIC_PUMP_CONTROL  "plant/pump/control"

// Pins
#define PIN_SOIL_MOISTURE   34   // Analog input (capacitive sensor)
#define PIN_DHT             4    // DHT22 data pin
#define PIN_PUMP_RELAY      26   // Relay IN pin (LOW = ON for most relay modules)

// Soil moisture thresholds (0-4095 raw ADC, lower = wetter for capacitive sensors)
#define MOISTURE_DRY_THRESHOLD   2800   // Below this → trigger watering
#define MOISTURE_WET_THRESHOLD   1500   // Above this (inverted) → stop watering

// Pump
#define PUMP_MAX_DURATION_MS  10000  // Max pump run time per cycle (10s safety limit)

// Sampling
#define SENSOR_INTERVAL_MS    5000   // Read & publish sensors every 5s
