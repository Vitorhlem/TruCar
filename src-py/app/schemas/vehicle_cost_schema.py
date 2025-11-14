from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.models.vehicle_cost_model import CostType

class VehicleCostBase(BaseModel):
    description: str
    amount: float
    date: date
    cost_type: CostType

class VehicleCostCreate(VehicleCostBase):
    """Schema para criar um custo (usado pelo endpoint de Custos)."""
    pass

class VehicleCostPublic(VehicleCostBase):
    """Schema para retornar um custo (usado em FinePublic)."""
    id: int
    vehicle_id: int
    fine_id: Optional[int] = None # Mostra o ID da multa vinculada, se houver

    class Config:
        from_attributes = True