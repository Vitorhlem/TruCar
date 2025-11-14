from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.part_model import PartCategory, InventoryItemStatus
# Não importe 'vehicle_schema' aqui no topo para evitar importação circular

# --- 1. Schema para o Item Físico (Individual) ---
class InventoryItemPublic(BaseModel):
    id: int
    item_identifier: int
    status: InventoryItemStatus
    part_id: int 
    organization_id: int
    installed_on_vehicle_id: Optional[int] = None
    created_at: datetime
    installed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- 2. Schemas Base para a Peça (Template) ---
class PartBase(BaseModel):
    name: str
    category: str 
    minimum_stock: int = 0
    part_number: Optional[str] = None
    brand: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    value: Optional[float] = None
    serial_number: Optional[str] = None
    lifespan_km: Optional[int] = None

class PartCreate(PartBase):
    initial_quantity: int = 0

class PartUpdate(PartBase):
    condition: Optional[str] = None 
    pass

# --- 3. Schema Público de LISTA (usado para GET /parts/ e agora para a nova página) ---
class PartListPublic(PartBase):
    id: int
    organization_id: int
    photo_url: Optional[str] = None
    invoice_url: Optional[str] = None
    stock: int = Field(0, description="Estoque disponível (calculado)")
    class Config:
        from_attributes = True

# --- 4. Schema Público de DETALHE (Template) ---
class PartPublic(PartBase):
    id: int
    organization_id: int
    photo_url: Optional[str] = None
    invoice_url: Optional[str] = None
    stock: int = Field(0, description="Estoque disponível (calculado)")
    items: List[InventoryItemPublic] = []
    class Config:
        from_attributes = True

# --- 5. Schema de DETALHES DO ITEM (Para a página 'item-details') ---
class InventoryItemDetails(InventoryItemPublic):
    part: PartListPublic 
    transactions: List['TransactionPublic'] = [] 

# --- 6. NOVOS SCHEMAS PARA A PÁGINA MESTRE (InventoryItemsPage) ---

# Schema mínimo para o veículo (para evitar importações circulares)
class _VehicleInfo(BaseModel):
    id: int
    brand: Optional[str] = None
    model: Optional[str] = None
    license_plate: Optional[str] = None
    identifier: Optional[str] = None
    class Config:
        from_attributes = True

# O schema para cada LINHA da nova tabela
class InventoryItemRow(InventoryItemPublic):
    part: PartListPublic # O template da peça (para sabermos o nome)
    installed_on_vehicle: Optional[_VehicleInfo] = None # O veículo onde está instalado

# O schema de resposta final (a página de itens)
class InventoryItemPage(BaseModel):
    total: int
    items: List[InventoryItemRow]
# --- FIM DOS NOVOS SCHEMAS ---

# --- 7. Recarregar os modelos ---
from .inventory_transaction_schema import TransactionPublic
InventoryItemPublic.model_rebuild()
PartPublic.model_rebuild()
PartListPublic.model_rebuild()
InventoryItemDetails.model_rebuild()
InventoryItemRow.model_rebuild()   # <-- Adicionado
InventoryItemPage.model_rebuild()  # <-- Adicionado