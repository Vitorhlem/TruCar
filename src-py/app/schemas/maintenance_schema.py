from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.models.maintenance_model import MaintenanceStatus, MaintenanceCategory
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic
from app.models.part_model import InventoryItemStatus # <-- 1. IMPORTAR STATUS DO ITEM

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

class MaintenanceRequestBase(BaseModel):
    problem_description: str
    vehicle_id: int
    category: MaintenanceCategory

class ReplaceComponentPayload(BaseModel):
    old_item_id: int
    new_item_id: int
    # O status de remoção é validado pelo enum
    old_item_status: InventoryItemStatus = InventoryItemStatus.FIM_DE_VIDA
    notes: Optional[str] = None

class ReplaceComponentResponse(BaseModel):

    success: bool = True
    message: str
    new_comment: MaintenanceCommentPublic # Retorna o comentário criado para rastreabilidade

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
    reporter: Optional[UserPublic] = None
    approver: Optional[UserPublic] = None
    vehicle: VehiclePublic
    manager_notes: Optional[str] = None
    comments: List[MaintenanceCommentPublic] = []
    
    model_config = { "from_attributes": True }