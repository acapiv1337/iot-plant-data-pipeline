import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from storage.database import get_db
from storage.models import PumpEvent, SensorReading

router = APIRouter()


# ── Readings ──────────────────────────────────────────────────────────────────

@router.get("/readings")
def get_readings(limit: int = 100, device_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(SensorReading).order_by(SensorReading.timestamp.desc())
    if device_id:
        q = q.filter(SensorReading.device_id == device_id)
    return q.limit(limit).all()


@router.get("/readings/latest")
def get_latest(device_id: str = "esp32-plant-01", db: Session = Depends(get_db)):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading


# ── Pump control ───────────────────────────────────────────────────────────────

class PumpCommand(BaseModel):
    action: str   # "on" | "off"
    device_id: str = "esp32-plant-01"


@router.post("/pump/control")
def control_pump(cmd: PumpCommand, db: Session = Depends(get_db)):
    if cmd.action not in ("on", "off"):
        raise HTTPException(status_code=400, detail="action must be 'on' or 'off'")

    # Publish MQTT command (client injected at startup)
    from api.main import mqtt_client
    payload = json.dumps({"action": cmd.action})
    mqtt_client.publish("plant/pump/control", payload)

    event = PumpEvent(device_id=cmd.device_id, action=cmd.action, trigger="manual")
    db.add(event)
    db.commit()
    return {"status": "sent", "action": cmd.action}


@router.get("/pump/events")
def get_pump_events(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(PumpEvent)
        .order_by(PumpEvent.timestamp.desc())
        .limit(limit)
        .all()
    )
