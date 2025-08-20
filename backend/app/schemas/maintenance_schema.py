from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.maintenance_request_model import MaintenanceStatus
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

# --- Schemas da Solicitação de Manutenção ---
class MaintenanceRequestBase(BaseModel):
    problem_description: str
    vehicle_id: int
    category: str # Adicionamos categoria aqui

class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass

class MaintenanceRequestUpdate(BaseModel):
    status: MaintenanceStatus
    manager_notes: Optional[str] = None

class MaintenanceRequestPublic(MaintenanceRequestBase):
    id: int
    status: MaintenanceStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    reporter: UserPublic
    approver: Optional[UserPublic] = None
    vehicle: VehiclePublic
    manager_notes: Optional[str] = None
    model_config = { "from_attributes": True }

# --- NOVOS SCHEMAS PARA OS COMENTÁRIOS (CHAT) ---
class MaintenanceCommentBase(BaseModel):
    comment_text: str

class MaintenanceCommentCreate(MaintenanceCommentBase):
    pass

class MaintenanceCommentPublic(MaintenanceCommentBase):
    id: int
    created_at: datetime
    user: UserPublic
    model_config = { "from_attributes": True }