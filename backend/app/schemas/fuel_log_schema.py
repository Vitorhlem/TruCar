from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

class FuelLogBase(BaseModel):
    odometer: int
    liters: float
    total_cost: float
    vehicle_id: int
    receipt_photo_url: Optional[str] = None

class FuelLogCreate(FuelLogBase):
    pass

class FuelLogPublic(FuelLogBase):
    id: int
    timestamp: datetime
    user: UserPublic
    vehicle: VehiclePublic # Incluímos o veículo para facilitar a exibição
    
    model_config = { "from_attributes": True }