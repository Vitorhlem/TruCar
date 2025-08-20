# backend/app/schemas/vehicle_schema.py

from pydantic import BaseModel, constr
from typing import Optional
from datetime import date

from app.models.vehicle_model import VehicleStatus

LicensePlateStr = constr(strip_whitespace=True, to_upper=True, min_length=7, max_length=8)

# Schema com campos que todos os veículos têm
class VehicleBase(BaseModel):
    brand: str
    model: str
    year: int
    photo_url: Optional[str] = None
    current_km: Optional[int] = 0
    current_engine_hours: Optional[float] = 0
    next_maintenance_date: Optional[date] = None
    next_maintenance_km: Optional[int] = None
    maintenance_notes: Optional[str] = None

# Schema para a CRIAÇÃO de um veículo. Aqui flexibilizamos a regra.
class VehicleCreate(VehicleBase):
    license_plate: Optional[LicensePlateStr] = None # TORNOU-SE OPCIONAL
    identifier: Optional[str] = None              # Adicionado para agronegócio, também opcional

# Schema para a ATUALIZAÇÃO
class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    photo_url: Optional[str] = None
    status: Optional[VehicleStatus] = None
    current_km: Optional[int] = None
    current_engine_hours: Optional[float] = None
    next_maintenance_date: Optional[date] = None
    next_maintenance_km: Optional[int] = None
    maintenance_notes: Optional[str] = None

# Schema de resposta PÚBLICA (o que a API retorna)
class VehiclePublic(VehicleBase):
    id: int
    status: VehicleStatus
    license_plate: Optional[LicensePlateStr] = None
    identifier: Optional[str] = None
    
    model_config = { "from_attributes": True }