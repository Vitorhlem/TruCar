from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.inventory_transaction_model import TransactionType
from app.schemas.user_schema import UserPublic
from app.schemas.vehicle_schema import VehiclePublic

# Schema para criar uma nova transação
class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    quantity: int # A quantidade sempre será positiva no payload
    notes: Optional[str] = None
    related_vehicle_id: Optional[int] = None
    related_user_id: Optional[int] = None

# Schema para exibir a transação na API
class TransactionPublic(BaseModel):
    id: int
    transaction_type: TransactionType
    quantity_change: int
    stock_after_transaction: int
    notes: Optional[str]
    timestamp: datetime
    
    # Relações que serão carregadas
    user: Optional[UserPublic] = None
    related_vehicle: Optional[VehiclePublic] = None
    related_user: Optional[UserPublic] = None

    class Config:
        from_attributes = True