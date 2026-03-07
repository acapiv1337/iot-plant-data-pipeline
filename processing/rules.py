from config.settings import settings


def should_start_pump(soil_moisture: float, pump_on: bool) -> bool:
    """Return True if pump should be turned on based on soil moisture."""
    return not pump_on and soil_moisture < settings.moisture_dry_threshold


def should_stop_pump(soil_moisture: float, pump_on: bool) -> bool:
    """Return True if pump should be turned off."""
    return pump_on and soil_moisture >= settings.moisture_wet_threshold


def evaluate(reading: dict) -> str | None:
    """
    Evaluate a sensor reading and return a pump action command or None.
    Returns: "on" | "off" | None
    """
    moisture = reading.get("soil_moisture", 100)
    pump_on  = reading.get("pump_on", False)

    if should_start_pump(moisture, pump_on):
        return "on"
    if should_stop_pump(moisture, pump_on):
        return "off"
    return None
