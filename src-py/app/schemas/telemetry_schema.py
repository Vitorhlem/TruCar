from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PointSchema(BaseModel):
    lat: float
    lng: float
    spd: Optional[float] = 0.0
    ts: int
    # Campos opcionais para eventos futuros
    acc_z: Optional[float] = 0.0
    pothole_detected: Optional[bool] = False

class TelemetryBatch(BaseModel):
    # Aceita tanto ID numérico (novo padrão ESP32) quanto token string (legado)
    vehicle_id: Optional[int] = None
    vehicle_token: Optional[str] = None
    
    events: List[Dict[str, Any]] = [] # Aceita lista vazia, necessário para o ESP32
    points: List[PointSchema]

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

TelemetryPayload = TelemetryBatch