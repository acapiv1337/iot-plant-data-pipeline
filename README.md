# IoT Plant Data Pipeline

IoT Watering Plant with Data Pipeline

## Architecture

```
Sensors --> Ingestion --> Processing --> Storage --> API --> Dashboard
```

## Project Structure

```

```

## Getting Started

### Prerequisites


### Setup

```bash
# Clone the repo
git clone https://github.com/acapiv1337/iot-plant-data-pipeline.git
cd iot-plant-data-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start services
docker-compose up -d
```

## Sensor Data Format

```json
{
  "device_id": "plant-sensor-01",
  "timestamp": "2026-03-07T09:00:00Z",
  "readings": {
    "soil_moisture": 42.5,
    "temperature": 22.1,
    "humidity": 65.0,
    "light_lux": 1200
  }
}
```

## License

MIT
