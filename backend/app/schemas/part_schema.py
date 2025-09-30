from pydantic import BaseModel
from typing import Optional

class PartBase(BaseModel):
    name: str
    category: str
    part_number: Optional[str] = None
    brand: Optional[str] = None
    stock: int
    min_stock: int
    location: Optional[str] = None
    notes: Optional[str] = None
    value: Optional[float] = None

class PartCreate(PartBase):
    pass

# --- CORREÇÃO APLICADA AQUI ---
# O PartUpdate agora define seus próprios campos, todos opcionais, e omite 'stock'.
class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    part_number: Optional[str] = None
    brand: Optional[str] = None
    min_stock: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    value: Optional[float] = None # --- ADICIONADO ---

# --- FIM DA CORREÇÃO ---

class PartPublic(PartBase):
    id: int
    photo_url: Optional[str] = None
    invoice_url: Optional[str] = None # --- ADICIONADO ---

    class Config:
        from_attributes = True