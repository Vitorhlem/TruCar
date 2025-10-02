from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .part_schema import PartPublic

# --- Schemas para Ações ---

class TireInstall(BaseModel):
    part_id: int
    position_code: str
    install_km: int = Field(..., ge=0)
    install_engine_hours: Optional[float] = Field(None, ge=0) # --- ADICIONADO ---

class TireRemove(BaseModel):
    removal_km: int = Field(..., ge=0)
    removal_engine_hours: Optional[float] = Field(None, ge=0)

class TireRotation(BaseModel):
    positions: dict[str, str]
    current_km: int = Field(..., gt=0)

# --- Schemas para Respostas ---

class VehicleTirePublic(BaseModel):
    id: int
    position_code: str
    installation_date: datetime
    install_km: int
    install_engine_hours: Optional[float] = None # --- ADICIONADO ---
    part: PartPublic

    class Config:
        from_attributes = True

class TireLayoutResponse(BaseModel):
    vehicle_id: int
    axle_configuration: Optional[str]
    tires: List[VehicleTirePublic]

