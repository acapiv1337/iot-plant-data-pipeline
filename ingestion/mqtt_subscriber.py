import asyncio
import json
import logging
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config.settings import settings
from processing import rules
from storage.database import SessionLocal
from storage.models import PumpEvent, SensorReading

logger = logging.getLogger(__name__)

# Injected by api/main.py so the subscriber can broadcast to WebSocket clients
_broadcast_callback = None


def set_broadcast_callback(cb):
    global _broadcast_callback
    _broadcast_callback = cb


def _save_reading(payload: dict):
    db = SessionLocal()
    try:
        reading = SensorReading(
            device_id=payload.get("device_id", "unknown"),
            timestamp=datetime.now(timezone.utc),
            soil_moisture=payload.get("soil_moisture"),
            temperature=payload.get("temperature"),
            humidity=payload.get("humidity"),
            pump_on=payload.get("pump_on", False),
        )
        db.add(reading)
        db.commit()
    finally:
        db.close()


def _save_pump_event(device_id: str, action: str, trigger: str = "auto"):
    db = SessionLocal()
    try:
        event = PumpEvent(device_id=device_id, action=action, trigger=trigger)
        db.add(event)
        db.commit()
    finally:
        db.close()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("MQTT connected")
        client.subscribe("plant/sensors")
        client.subscribe("plant/pump/status")
    else:
        logger.error("MQTT connect failed rc=%s", rc)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.debug("MQTT [%s]: %s", msg.topic, payload)

        if msg.topic == "plant/sensors":
            _save_reading(payload)

            # Evaluate auto-watering rules
            action = rules.evaluate(payload)
            if action:
                device_id = payload.get("device_id", "unknown")
                command   = json.dumps({"action": action})
                client.publish("plant/pump/control", command)
                _save_pump_event(device_id, action, trigger="auto")
                logger.info("Auto pump command: %s → %s", device_id, action)

            # Broadcast to WebSocket clients
            if _broadcast_callback:
                asyncio.run_coroutine_threadsafe(
                    _broadcast_callback(payload),
                    asyncio.get_event_loop(),
                )

    except Exception:
        logger.exception("Error processing MQTT message")


def create_client() -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    return client
