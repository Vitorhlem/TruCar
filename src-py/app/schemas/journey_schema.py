from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum

from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

class ImplementPublic(BaseModel):
    id: int
    name: str
    model: str
    
    model_config = { "from_attributes": True }

class JourneyType(str, enum.Enum):
    SPECIFIC_DESTINATION = 'specific_destination'
    FREE_ROAM = 'free_roam'

class JourneyBase(BaseModel):
    trip_type: JourneyType
    destination_address: Optional[str] = None
    trip_description: Optional[str] = None

class JourneyCreate(JourneyBase):
    vehicle_id: int
    start_mileage: Optional[int] = None
    start_engine_hours: Optional[float] = None
    implement_id: Optional[int] = None
    
    destination_street: Optional[str] = None
    destination_neighborhood: Optional[str] = None
    destination_city: Optional[str] = None
    destination_state: Optional[str] = None
    destination_cep: Optional[str] = None

class JourneyUpdate(BaseModel):
    end_mileage: Optional[int] = None
    end_engine_hours: Optional[float] = None

class JourneyPublic(JourneyBase):
    id: int
    is_active: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    start_mileage: int | None
    end_mileage: Optional[int] = None
    start_engine_hours: Optional[float] = None
    end_engine_hours: Optional[float] = None
    driver: UserPublic
    vehicle: VehiclePublic
    implement: Optional[ImplementPublic] = None
    
    destination_street: Optional[str] = None
    destination_neighborhood: Optional[str] = None
    destination_city: Optional[str] = None
    destination_state: Optional[str] = None
    destination_cep: Optional[str] = None
    
    model_config = { "from_attributes": True }

class EndJourneyResponse(BaseModel):
    journey: JourneyPublic
    vehicle: VehiclePublic
