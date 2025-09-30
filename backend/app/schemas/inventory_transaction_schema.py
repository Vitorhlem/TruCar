from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.inventory_transaction_model import TransactionType
# --- GARANTIR ESTES IMPORTS ---
from app.schemas.user_schema import UserPublic
from app.schemas.vehicle_schema import VehiclePublic
from app.schemas.part_schema import PartPublic

# Schema para criar uma nova transação
class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    quantity: int # A quantidade sempre será positiva no payload
    notes: Optional[str] = None
    related_vehicle_id: Optional[int] = None
    related_user_id: Optional[int] = None

# Schema para exibir a transação na API (Resposta)
class TransactionPublic(BaseModel):
    id: int
    transaction_type: TransactionType
    quantity_change: int
    stock_after_transaction: int
    notes: Optional[str]
    timestamp: datetime
    
    # Relações que precisam de ser carregadas e validadas
    user: Optional[UserPublic] = None
    related_vehicle: Optional[VehiclePublic] = None
    related_user: Optional[UserPublic] = None
    part: Optional[PartPublic] = None

    class Config:
        from_attributes = True # Essencial para converter modelos SQLAlchemy para Pydantic