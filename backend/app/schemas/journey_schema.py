from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

from app.models.journey_model import JourneyType
from app.models.maintenance_request_model import MaintenanceStatus, MaintenanceCategory
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

# --- Schemas Base ---
class JourneyBase(BaseModel):
    trip_type: JourneyType
    destination_address: Optional[str] = None
    trip_description: Optional[str] = None

class JourneyCreate(JourneyBase):
    vehicle_id: int
    start_mileage: int
    start_mileage: Optional[int] = None # Torna-se opcional
    start_engine_hours: Optional[float] = None # Novo campo opcional

class JourneyUpdate(BaseModel):
    end_mileage: int
     
    end_mileage: Optional[int] = None # Torna-se opcional
    end_engine_hours: Optional[float] = None # Novo campo opcional

# --- Schema Público (usado em respostas da API) ---
# Definido ANTES de ser usado por outros schemas
class JourneyPublic(JourneyBase):
    id: int
    is_active: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    start_mileage: int
    end_mileage: Optional[int] = None
    driver: UserPublic
    vehicle: VehiclePublic
    
    model_config = { "from_attributes": True }

# --- Schema da Resposta de Finalização ---
class EndJourneyResponse(BaseModel):
    journey: JourneyPublic
    vehicle: VehiclePublic

# --- Schemas de Manutenção ---
class MaintenanceRequestBase(BaseModel):
    problem_description: str
    vehicle_id: int
    category: MaintenanceCategory

class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass

class MaintenanceRequestUpdate(BaseModel):
    status: MaintenanceStatus
    manager_notes: Optional[str] = None

class MaintenanceCommentBase(BaseModel):
    comment_text: str
    file_url: Optional[str] = None

class MaintenanceCommentCreate(MaintenanceCommentBase):
    pass

class MaintenanceCommentPublic(MaintenanceCommentBase):
    id: int
    created_at: datetime
    user: UserPublic
    model_config = { "from_attributes": True }

class MaintenanceRequestPublic(MaintenanceRequestBase):
    id: int
    status: MaintenanceStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    reporter: UserPublic
    approver: Optional[UserPublic] = None
    vehicle: VehiclePublic
    manager_notes: Optional[str] = None
    comments: List[MaintenanceCommentPublic] = []
    model_config = { "from_attributes": True }