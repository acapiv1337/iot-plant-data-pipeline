from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883

    # Database
    database_url: str = "sqlite:///./plant.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Auto-watering
    moisture_dry_threshold: float = 30.0   # % — pump on below this
    moisture_wet_threshold: float = 60.0   # % — pump off above this

    class Config:
        env_file = ".env"


settings = Settings()
