from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

from app.models.maintenance_model import MaintenanceStatus, MaintenanceCategory
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic
from .vehicle_component_schema import VehicleComponentPublic 
from app.models.part_model import InventoryItemStatus 

class MaintenanceCommentBase(BaseModel):
    comment_text: str
    file_url: Optional[str] = None

class MaintenanceCommentCreate(MaintenanceCommentBase):
    pass

class MaintenanceCommentPublic(MaintenanceCommentBase):
    id: int
    created_at: datetime
    user: Optional[UserPublic] = None 
    model_config = { "from_attributes": True }


class MaintenancePartChangePublic(BaseModel):
    id: int
    timestamp: datetime
    user: UserPublic
    notes: Optional[str] = None
    
    # --- ALTERAÇÃO AQUI: Agora é Optional ---
    component_removed: Optional[VehicleComponentPublic] = None
    # --- FIM DA ALTERAÇÃO ---
    
    component_installed: VehicleComponentPublic 
    
    is_reverted: bool
    
    model_config = { "from_attributes": True }


class ReplaceComponentPayload(BaseModel):
    component_to_remove_id: int 
    new_item_id: int 
    old_item_status: InventoryItemStatus = InventoryItemStatus.FIM_DE_VIDA
    notes: Optional[str] = None

class ReplaceComponentResponse(BaseModel):
    success: bool = True
    message: str
    part_change_log: MaintenancePartChangePublic 
    new_comment: MaintenanceCommentPublic

# --- NOVOS SCHEMAS PARA INSTALAÇÃO ---
class InstallComponentPayload(BaseModel):
    new_item_id: int
    notes: Optional[str] = None

class InstallComponentResponse(BaseModel):
    success: bool = True
    message: str
    part_change_log: MaintenancePartChangePublic 
    new_comment: MaintenanceCommentPublic
# --- FIM DOS NOVOS SCHEMAS ---

class MaintenanceRequestBase(BaseModel):
    problem_description: str
    vehicle_id: int
    category: MaintenanceCategory
    maintenance_type: str = "CORRETIVA" 

class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass

class MaintenanceRequestUpdate(BaseModel):
    next_maintenance_date: Optional[date] = None
    next_maintenance_km: Optional[float] = None
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
    services: List[MaintenanceServiceItemPublic] = []
    comments: List[MaintenanceCommentPublic] = []
    maintenance_type: Optional[str] = "CORRETIVA"
    part_changes: List[MaintenancePartChangePublic] = []
    
    model_config = { "from_attributes": True }

class MaintenanceServiceItemBase(BaseModel):
    description: str
    cost: float
    provider_name: Optional[str] = None
    notes: Optional[str] = None

class MaintenanceServiceItemCreate(MaintenanceServiceItemBase):
    pass

class MaintenanceServiceItemPublic(MaintenanceServiceItemBase):
    id: int
    created_at: datetime
    added_by_id: int
    model_config = { "from_attributes": True }