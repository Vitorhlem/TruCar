# backend/app/schemas/implement_schema.py

from pydantic import BaseModel
from typing import Optional

# Schema base com os campos comuns
class ImplementBase(BaseModel):
    name: str
    brand: str
    model: str
    year: int
    identifier: Optional[str] = None

# Schema para a CRIAÇÃO de um novo implemento
class ImplementCreate(ImplementBase):
    pass

# Schema para a ATUALIZAÇÃO de um implemento (todos os campos são opcionais)
class ImplementUpdate(ImplementBase):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None

# Schema para a RESPOSTA PÚBLICA da API (o que é enviado para o front-end)
class ImplementPublic(ImplementBase):
    id: int
    
    model_config = { "from_attributes": True }