# ARQUIVO: backend/app/schemas/freight_order_schema.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.freight_order_model import FreightStatus
from app.models.stop_point_model import StopPointType, StopPointStatus
from .client_schema import ClientPublic
from .vehicle_schema import VehiclePublic
from .user_schema import UserPublic

# --- Schemas para Pontos de Parada (StopPoint) ---

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

# --- Schemas para Ordens de Frete (FreightOrder) ---

class FreightOrderClaim(BaseModel):
    vehicle_id: int

class FreightOrderBase(BaseModel):
    description: Optional[str] = None
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    client_id: int

class FreightOrderCreate(FreightOrderBase):
    # Ao criar um frete, passamos a lista de paradas junto
    stop_points: List[StopPointCreate]

class FreightOrderUpdate(BaseModel):
    # O que um gestor pode atualizar em um frete existente
    description: Optional[str] = None
    status: Optional[FreightStatus] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None

class FreightOrderPublic(FreightOrderBase):
    id: int
    status: FreightStatus
    
    # Retorna os objetos completos, não apenas os IDs
    client: ClientPublic
    vehicle: Optional[VehiclePublic] = None
    driver: Optional[UserPublic] = None
    stop_points: List[StopPointPublic] = []
    
    model_config = { "from_attributes": True }