"""Point d'entrée FastAPI du microservice MS6 - Validateur de capteurs."""

from fastapi import FastAPI
from pydantic import BaseModel

from validator import SensorValidator

app = FastAPI(title="MS6 - Sensor Validator", version="1.0.0")
validator = SensorValidator()


class SensorReading(BaseModel):
    """Payload d'une mesure capteur."""

    sensor: str
    value: float


@app.get("/health")
def health() -> dict:
    """Vérifie que le service est opérationnel."""
    return {"status": "healthy", "service": "ms6-validateur"}


@app.post("/validate")
def validate(reading: SensorReading) -> dict:
    """Valide une mesure capteur et retourne son niveau de criticité."""
    return validator.validate(reading.sensor, reading.value)
