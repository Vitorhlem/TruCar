from pydantic import BaseModel, constr
from typing import Optional

from app.models.vehicle_model import VehicleStatus

# constr(strip_whitespace=True, to_upper=True, min_length=7, max_length=8)
# Validador para garantir que a placa seja sempre armazenada em maiúsculas,
# sem espaços extras e com um tamanho razoável.
LicensePlateStr = constr(strip_whitespace=True, to_upper=True, min_length=7, max_length=8)

# --- Schemas Base ---

class VehicleBase(BaseModel):
    """Schema base para veículos, com os campos principais."""
    brand: str
    model: str
    license_plate: LicensePlateStr
    year: int

# --- Schemas para Operações Específicas ---

class VehicleCreate(VehicleBase):
    """Schema usado para criar um novo veículo. O status será 'available' por padrão."""
    photo_url: Optional[str] = None

class VehicleUpdate(BaseModel):
    """Schema usado para atualizar um veículo. Todos os campos são opcionais."""
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    photo_url: Optional[str] = None
    status: Optional[VehicleStatus] = None


# --- Schema para Resposta da API ---

class VehiclePublic(VehicleBase):
    """
    Schema público do veículo, retornado pela API.
    """
    id: int
    status: VehicleStatus
    photo_url: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }