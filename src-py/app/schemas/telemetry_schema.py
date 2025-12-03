from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TelemetryPayload(BaseModel):
    device_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    engine_hours: float
    fuel_level: Optional[float] = None
    error_codes: Optional[List[str]] = None

class TelemetryEvent(BaseModel):
    type: str 
    lat: float
    lng: float
    val: float 
    ts: int

class TelemetryPoint(BaseModel):
    lat: float
    lng: float
    spd: float
    ts: int

class TelemetryPacket(BaseModel):
    vehicle_id: int
    journey_id: Optional[int] = None
    points: List[TelemetryPoint]
    events: List[TelemetryEvent]