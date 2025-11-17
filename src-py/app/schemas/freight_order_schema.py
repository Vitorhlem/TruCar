
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.freight_order_model import FreightStatus
from app.models.stop_point_model import StopPointType, StopPointStatus
from .client_schema import ClientPublic
from .vehicle_schema import VehiclePublic
from .user_schema import UserPublic


class StopPointBase(BaseModel):
    sequence_order: int
    type: StopPointType
    address: str
    cargo_description: Optional[str] = None
    scheduled_time: datetime

class StopPointCreate(StopPointBase):
    pass

class StopPointPublic(StopPointBase):
    id: int
    status: StopPointStatus
    actual_arrival_time: Optional[datetime] = None
    
    model_config = { "from_attributes": True }


class FreightOrderClaim(BaseModel):
    vehicle_id: int

class FreightOrderBase(BaseModel):
    description: Optional[str] = None
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    client_id: int

class FreightOrderCreate(FreightOrderBase):
    stop_points: List[StopPointCreate]

class FreightOrderUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[FreightStatus] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None

class FreightOrderPublic(FreightOrderBase):
    id: int
    status: FreightStatus
    
    client: ClientPublic
    vehicle: Optional[VehiclePublic] = None
    driver: Optional[UserPublic] = None
    stop_points: List[StopPointPublic] = []
    
    model_config = { "from_attributes": True }