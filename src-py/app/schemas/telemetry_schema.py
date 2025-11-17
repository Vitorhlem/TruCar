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
    error_codes: Optional[List[str]] = None