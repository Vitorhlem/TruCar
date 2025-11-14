from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic
from app.models.notification_model import NotificationType # Importar o Enum

class NotificationBase(BaseModel):
    message: str
    is_read: bool

# --- SCHEMA PUBLIC ATUALIZADO ---
class NotificationPublic(NotificationBase):
    id: int
    created_at: datetime
    
    # Novos campos adicionados para o frontend
    notification_type: NotificationType
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    
    # Relações existentes
    user: Optional[UserPublic] = None
    vehicle: Optional[VehiclePublic] = None
    
    class Config:
        from_attributes = True
# --- FIM DA ATUALIZAÇÃO ---

# Schema para criação (não é usado diretamente pela API, mas internamente)
class NotificationCreate(BaseModel):
    user_id: int
    organization_id: int
    message: str
    notification_type: NotificationType
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    related_vehicle_id: Optional[int] = None