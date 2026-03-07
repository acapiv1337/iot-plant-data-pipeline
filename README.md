# IoT Plant Data Pipeline

IoT Watering Plant with Data Pipeline

## Architecture

```
ESP32 (sensors + pump) --> MQTT Broker --> Ingestion --> Processing --> Storage --> API --> Dashboard
```

- **ESP32** reads soil moisture, temperature, humidity and controls a water pump via relay
- **MQTT** (Mosquitto) is the realtime message bus between device and backend
- **Ingestion** subscribes to MQTT topics and stores readings in the database
- **Processing** evaluates auto-watering rules (pump on/off based on moisture thresholds)
- **API** (FastAPI) exposes REST endpoints and a WebSocket for realtime dashboard updates
- **Dashboard** shows live sensor charts and manual pump control

## Project Structure

```
iot-plant-data-pipeline/
├── firmware/
│   └── main/
│       ├── main.ino        # ESP32 sketch (sensors, pump, MQTT publish)
│       └── config.h        # WiFi, MQTT, pin, threshold config
├── ingestion/
│   └── mqtt_subscriber.py  # MQTT client — saves readings, triggers rules
├── processing/
│   └── rules.py            # Auto-watering logic
├── storage/
│   ├── database.py         # SQLAlchemy engine & session
│   └── models.py           # SensorReading, PumpEvent models
├── api/
│   ├── main.py             # FastAPI app + WebSocket endpoint
│   ├── routes.py           # REST: /readings, /pump/control, /pump/events
│   └── websocket.py        # WebSocket connection manager
├── dashboard/
│   ├── index.html          # Live sensor dashboard
│   └── app.js              # Chart.js + WebSocket + pump controls
├── config/
│   └── settings.py         # Pydantic settings (env-driven)
├── mosquitto/
│   └── config/
│       └── mosquitto.conf  # MQTT broker config
├── tests/
├── docker-compose.yml      # Mosquitto + backend services
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Arduino IDE with ESP32 board support

### Arduino Libraries (install via Library Manager)
- `PubSubClient` by Nick O'Leary
- `ArduinoJson` by Benoit Blanchon
- `DHT sensor library` by Adafruit

### Setup

```bash
# Clone the repo
git clone https://github.com/acapiv1337/iot-plant-data-pipeline.git
cd iot-plant-data-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env config
cp .env.example .env

# Start MQTT broker + backend
docker-compose up -d

# Or run backend locally
uvicorn api.main:app --reload
```

Dashboard → [http://localhost:8000](http://localhost:8000)

API docs → [http://localhost:8000/docs](http://localhost:8000/docs)

### Flash ESP32

1. Open `firmware/main/main.ino` in Arduino IDE
2. Edit `config.h` — set your WiFi credentials and backend IP
3. Select board: **ESP32 Dev Module**
4. Flash

## Sensor Data (MQTT topic: `plant/sensors`)

```json
{
  "device_id": "esp32-plant-01",
  "soil_moisture": 42.5,
  "temperature": 22.1,
  "humidity": 65.0,
  "pump_on": false
}
```

## Auto-Watering Rules

| Condition | Action |
|-----------|--------|
| `soil_moisture < 30%` | Pump ON |
| `soil_moisture >= 60%` | Pump OFF |
| Pump runs > 10s | Force stop (safety) |

Thresholds are configurable via `.env` (`MOISTURE_DRY_THRESHOLD`, `MOISTURE_WET_THRESHOLD`).

## License

MIT
