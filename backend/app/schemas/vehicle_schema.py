# backend/app/schemas/vehicle_schema.py

from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import date
from app.models.vehicle_model import VehicleStatus

# Tipo para validar o formato da placa (pode ajustar se necessário)
LicensePlateStr = constr(strip_whitespace=True, to_upper=True)

# Schema base com os campos comuns a todas as operações de veículo
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
    identifier: Optional[str] = None
    license_plate: Optional[LicensePlateStr] = None

# Schema para a CRIAÇÃO de um veículo
class VehicleCreate(VehicleBase):
    pass

# Schema para a ATUALIZAÇÃO de um veículo (todos os campos são opcionais)
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

# Schema para a RESPOSTA PÚBLICA da API
class VehiclePublic(VehicleBase):
    id: int
    status: VehicleStatus
    
    model_config = { "from_attributes": True }

# O SCHEMA QUE ESTAVA EM FALTA:
# Define a estrutura para respostas paginadas
class PaginatedVehicles(BaseModel):
    total: int
    items: List[VehiclePublic]