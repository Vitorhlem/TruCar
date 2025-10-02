from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .part_schema import PartPublic

# --- Schemas para Ações ---

class TireInstall(BaseModel):
    part_id: int # ID do pneu no inventário
    position_code: str # Ex: "1D" (Eixo 1, Direito)
    install_km: int = Field(..., gt=0) # KM atual do veículo

class TireRotation(BaseModel):
    # Um dicionário mapeando a posição atual para a nova posição
    # Ex: { "1E": "2E", "2E": "1E" }
    positions: dict[str, str]
    current_km: int = Field(..., gt=0)

# --- Schemas para Respostas ---

class VehicleTirePublic(BaseModel):
    id: int
    position_code: str
    installation_date: datetime # CORRIGIDO: O nome do campo estava 'install_date'
    install_km: int
    part: PartPublic # Detalhes completos do pneu

    class Config:
        from_attributes = True

class TireLayoutResponse(BaseModel):
    vehicle_id: int
    axle_configuration: Optional[str]
    tires: List[VehicleTirePublic]
