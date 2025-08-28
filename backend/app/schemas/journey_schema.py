# app/schemas/journey_schema.py

from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum

# Importa outros schemas que são usados nas respostas
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

# --- INÍCIO DA MODIFICAÇÃO 1 (NOVO SCHEMA) ---
# Crie este schema mínimo para o implemento para evitar dependências circulares
# e para usar na resposta da API.
class ImplementPublic(BaseModel):
    id: int
    name: str
    model: str
    
    model_config = { "from_attributes": True }
# --- FIM DA MODIFICAÇÃO 1 ---


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
    # --- INÍCIO DA MODIFICAÇÃO 2 (ADICIONAR CAMPO) ---
    implement_id: Optional[int] = None # Permite que o frontend envie o ID do implemento
    # --- FIM DA MODIFICAÇÃO 2 ---

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
    # --- INÍCIO DA MODIFICAÇÃO 3 (ADICIONAR RELACIONAMENTO) ---
    implement: Optional[ImplementPublic] = None # Retorna os dados do implemento associado
    # --- FIM DA MODIFICAÇÃO 3 ---
    
    model_config = { "from_attributes": True }

class EndJourneyResponse(BaseModel):
    journey: JourneyPublic
    vehicle: VehiclePublic