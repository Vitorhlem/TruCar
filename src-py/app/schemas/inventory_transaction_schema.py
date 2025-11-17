
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.inventory_transaction_model import TransactionType

from .user_schema import UserPublic

class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    quantity: int 
    notes: Optional[str] = None
    related_vehicle_id: Optional[int] = None
    related_user_id: Optional[int] = None

class TransactionPublic(BaseModel):
    id: int
    transaction_type: TransactionType
    notes: Optional[str]
    timestamp: datetime
    
    user: Optional[UserPublic] = None
    related_vehicle: Optional['VehiclePublic'] = None
    related_user: Optional[UserPublic] = None
    
    item: Optional['InventoryItemPublic'] = None 
    
    part: Optional['PartListPublic'] = Field(None, alias="part_template")
    class Config:
        from_attributes = True

class TransactionForComponent(BaseModel):
    id: int
    user: Optional[UserPublic] = None # Carrega apenas o usuário
    item: Optional['InventoryItemPublic'] = None 

    class Config:
        from_attributes = True

from .part_schema import InventoryItemPublic, PartPublic, PartListPublic
from .vehicle_schema import VehiclePublic # Importamos aqui

TransactionPublic.model_rebuild()
TransactionForComponent.model_rebuild()
