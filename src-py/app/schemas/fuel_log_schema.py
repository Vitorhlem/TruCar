from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic
from app.models.fuel_log_model import VerificationStatus

class FuelLogBase(BaseModel):
    odometer: int
    liters: float
    total_cost: float
    vehicle_id: int
    receipt_photo_url: Optional[str] = None

class FuelLogCreate(FuelLogBase):
    user_id: Optional[int] = None  # <-- ADICIONE ESTA LINHA

class FuelLogUpdate(BaseModel):
    odometer: Optional[int] = None
    liters: Optional[float] = None
    total_cost: Optional[float] = None
    vehicle_id: Optional[int] = None
    receipt_photo_url: Optional[str] = None

class FuelLogPublic(FuelLogBase):
    id: int
    timestamp: datetime
    user: UserPublic
    vehicle: VehiclePublic
    
    verification_status: VerificationStatus
    provider_name: Optional[str] = None
    gas_station_name: Optional[str] = None
    source: str # MANUAL ou INTEGRATION
    
    model_config = { "from_attributes": True }

class FuelProviderTransaction(BaseModel):
    transaction_id: str
    vehicle_license_plate: str
    driver_employee_id: str # Usamos o ID do funcionário em vez do CPF
    timestamp: datetime
    liters: float
    total_cost: float
    gas_station_name: str
    gas_station_latitude: float
    gas_station_longitude: float

