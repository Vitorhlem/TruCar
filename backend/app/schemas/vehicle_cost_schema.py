from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.models.vehicle_cost_model import CostType
from .vehicle_schema import VehiclePublic  # <-- 1. IMPORTAR O SCHEMA DO VEÍCULO

# Propriedades base de um custo de veículo
class VehicleCostBase(BaseModel):
    description: str
    amount: float
    date: date
    cost_type: CostType

# Propriedades recebidas ao criar um novo custo
class VehicleCostCreate(VehicleCostBase):
    pass

# Propriedades retornadas pela API
class VehicleCostPublic(VehicleCostBase):
    id: int
    vehicle_id: int
    vehicle: Optional[VehiclePublic] = None  # <-- 2. ADICIONAR O VEÍCULO ANINHADO

    class Config:
        from_attributes = True