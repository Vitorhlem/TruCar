# backend/app/schemas/implement_schema.py

from pydantic import BaseModel, Field
from app.models.implement_model import ImplementStatus
from typing import Optional
# --- 1. ADICIONE 'date' ---
from datetime import date

# Schema base com os campos comuns
class ImplementBase(BaseModel):
    name: str
    brand: str
    model: str
    year: int
    identifier: Optional[str] = None
    status: str = Field(default=ImplementStatus.AVAILABLE)
    
    # --- 2. ADICIONE OS NOVOS CAMPOS AQUI ---
    # O 'type' já foi adicionado na etapa anterior
    type: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_value: Optional[float] = None
    notes: Optional[str] = None
    # --- FIM DA ADIÇÃO ---


# Schema para a CRIAÇÃO de um novo implemento
class ImplementCreate(ImplementBase):
    pass

# Schema para a ATUALIZAÇÃO de um implemento (todos os campos são opcionais)
class ImplementUpdate(ImplementBase):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None
    
    # --- 3. ADICIONE OS CAMPOS NA ATUALIZAÇÃO TAMBÉM ---
    type: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_value: Optional[float] = None
    notes: Optional[str] = None


# Schema para a RESPOSTA PÚBLICA da API (o que é enviado para o front-end)
class ImplementPublic(ImplementBase):
    id: int
    
    # Os novos campos já estão incluídos por herdar de ImplementBase
    
    model_config = { "from_attributes": True }