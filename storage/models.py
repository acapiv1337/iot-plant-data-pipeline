from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Column
from storage.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id            = Column(Integer, primary_key=True, index=True)
    device_id     = Column(String, index=True)
    timestamp     = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    soil_moisture = Column(Float)   # percentage 0-100
    temperature   = Column(Float)   # Celsius
    humidity      = Column(Float)   # percentage 0-100
    pump_on       = Column(Boolean, default=False)


class PumpEvent(Base):
    __tablename__ = "pump_events"

    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    action    = Column(String)   # "on" | "off"
    trigger   = Column(String)   # "auto" | "manual"
