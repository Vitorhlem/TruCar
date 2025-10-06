# Em backend/app/schemas/fine_schema.py

from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.models.fine_model import FineStatus
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

class FineBase(BaseModel):
    description: str
    date: date
    value: float
    status: FineStatus = FineStatus.PENDING
    vehicle_id: int
    driver_id: Optional[int] = None
    infraction_code: Optional[str] = None

class FineCreate(FineBase):
    pass

class FineUpdate(BaseModel):
    description: Optional[str] = None
    date: Optional[date] = None
    value: Optional[float] = None
    status: Optional[FineStatus] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    infraction_code: Optional[str] = None

class FinePublic(FineBase):
    id: int
    vehicle: Optional[VehiclePublic] = None
    driver: Optional[UserPublic] = None

    class Config:
        from_attributes = True