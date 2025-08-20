from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

class MaintenanceCommentBase(BaseModel):
    comment_text: str
    file_url: Optional[str] = None # Adiciona o campo de anexo

class MaintenanceCommentCreate(MaintenanceCommentBase):
    pass

class MaintenanceCommentPublic(MaintenanceCommentBase):
    id: int
    created_at: datetime
    user: UserPublic
    model_config = { "from_attributes": True }


class NotificationBase(BaseModel):
    message: str
    is_read: bool

class NotificationPublic(NotificationBase):
    id: int
    created_at: datetime
    user: Optional[UserPublic] = None
    vehicle: Optional[VehiclePublic] = None
    
    model_config = { "from_attributes": True }

    