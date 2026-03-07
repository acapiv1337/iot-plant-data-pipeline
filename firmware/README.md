# ESP32-CAM Plant Monitor

ESP32-CAM AI Thinker running a camera web server with DHT11 temperature/humidity and soil moisture sensor readings.

## Features

- Live camera stream (MJPEG) via browser
- Single image capture
- Camera settings control (brightness, contrast, frame size, etc.)
- DHT11 temperature and humidity readings every 2 seconds
- Soil moisture sensor (dry/wet) readings every 2 seconds

## Hardware

- ESP32-CAM AI Thinker (OV2640 camera)
- DHT11 temperature & humidity sensor (3-pin module)
- Soil moisture sensor module (digital DO output)

## Wiring

| Sensor        | Sensor Pin | ESP32-CAM Pin |
|---------------|------------|---------------|
| DHT11         | VCC        | 3.3V          |
| DHT11         | GND        | GND           |
| DHT11         | DATA       | IO14 (GPIO14) |
| Soil Sensor   | VCC        | 3.3V          |
| Soil Sensor   | GND        | GND           |
| Soil Sensor   | DO         | IO13 (GPIO13) |

> Use 3.3V for both sensors. Using 5V on the DATA pin can damage ESP32 GPIO.

## Software Setup

- Framework: Arduino (via PlatformIO)
- Platform: espressif32 @ 6.13.0
- Libraries: Adafruit DHT sensor library, Adafruit Unified Sensor

### platformio.ini

```ini
[env:esp32cam]
platform = espressif32@6.13.0
board = esp32cam
framework = arduino
monitor_speed = 115200
monitor_rts = 0
monitor_dtr = 0
board_build.partitions = huge_app.csv
build_flags =
    -DBOARD_HAS_PSRAM
    -mfix-esp32-psram-cache-issue
lib_deps =
    adafruit/DHT sensor library@^1.4.6
    adafruit/Adafruit Unified Sensor@^1.1.14
```

## Configuration

Edit `src/main.cpp` to set your WiFi credentials:

```cpp
const char* ssid = "your_wifi_name";
const char* password = "your_wifi_password";
```

## Usage

1. Build and upload via PlatformIO
2. Open Serial Monitor at 115200 baud
3. Wait for IP address to appear, e.g. `Camera Ready! Use 'http://192.168.x.x'`
4. Open that IP in a browser for the camera UI
5. Sensor readings print to serial monitor every 2 seconds:

```
Temp: 28.0 C  Humidity: 65.0 %  Soil: DRY
```

## Web Endpoints

| URL                        | Description              |
|----------------------------|--------------------------|
| `http://<ip>/`             | Camera control UI        |
| `http://<ip>/capture`      | Single JPEG snapshot     |
| `http://<ip>:81/stream`    | MJPEG live stream        |
| `http://<ip>/status`       | Camera settings JSON     |
| `http://<ip>/control`      | Change camera settings   |
