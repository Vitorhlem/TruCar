# ARQUIVO: app/schemas/inventory_transaction_schema.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.inventory_transaction_model import TransactionType

# --- 1. IMPORTAR OS SCHEMAS QUE SÃO SEGUROS (sem import circular) ---
from .user_schema import UserPublic
# NÃO importe part_schema ou vehicle_schema aqui

# --- 2. Schema para criar uma nova transação (Sem mudança) ---
class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    quantity: int 
    notes: Optional[str] = None
    related_vehicle_id: Optional[int] = None
    related_user_id: Optional[int] = None

# --- 3. Schema de Resposta com 'Forward References' (strings) ---
class TransactionPublic(BaseModel):
    id: int
    transaction_type: TransactionType
    notes: Optional[str]
    timestamp: datetime
    
    user: Optional[UserPublic] = None
    # Usamos string 'VehiclePublic' para evitar importação
    related_vehicle: Optional['VehiclePublic'] = None
    related_user: Optional[UserPublic] = None
    
    # Usamos strings 'InventoryItemPublic' e 'PartPublic'
    item: Optional['InventoryItemPublic'] = None 
    
    # --- A MUDANÇA ESTÁ AQUI ---
    # ANTES:
    # part: Optional['PartPublic'] = Field(None, alias="part_template")
    # DEPOIS: Usamos o schema de LISTA, que não é recursivo
    part: Optional['PartListPublic'] = Field(None, alias="part_template")
    class Config:
        from_attributes = True

# --- 4. NOVO SCHEMA SIMPLIFICADO (A CORREÇÃO) ---
class TransactionForComponent(BaseModel):
    id: int
    user: Optional[UserPublic] = None # Carrega apenas o usuário
    # Adicionamos 'item' aqui para podermos pegar o 'item_identifier' na VehicleDetailsPage
    item: Optional['InventoryItemPublic'] = None 

    class Config:
        from_attributes = True

# --- 5. CORREÇÃO DO IMPORT CIRCULAR: Importar e Reconstruir ---
from .part_schema import InventoryItemPublic, PartPublic, PartListPublic
from .vehicle_schema import VehiclePublic # Importamos aqui

TransactionPublic.model_rebuild()
TransactionForComponent.model_rebuild()
