# backend/app/schemas/telemetry_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TelemetryPayload(BaseModel):
    device_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    engine_hours: float
    fuel_level: Optional[float] = None
    # Códigos de erro do motor, se houver
    error_codes: Optional[List[str]] = None