from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# --- SCHEMA DOS PONTOS ---
class PointSchema(BaseModel):
    lat: float
    lng: float
    spd: Optional[float] = 0.0
    ts: int
    # Campos opcionais para eventos
    acc_z: Optional[float] = 0.0
    pothole_detected: Optional[bool] = False

# --- SCHEMA DO PACOTE (BATCH) ---
class TelemetryBatch(BaseModel):
    # Aceita tanto ID numérico (novo código) quanto token string (legado)
    vehicle_id: Optional[int] = None
    vehicle_token: Optional[str] = None
    
    events: List[Dict[str, Any]] = [] # Aceita lista vazia de eventos
    points: List[PointSchema]

# --- COMPATIBILIDADE (FIX DO ERRO) ---
# Isso garante que arquivos antigos (como crud_vehicle.py) encontrem o que procuram
TelemetryPayload = TelemetryBatch