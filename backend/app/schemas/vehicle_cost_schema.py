from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.models.vehicle_cost_model import CostType

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

    model_config = { "from_attributes": True }