# backend/app/schemas/organization_schema.py

from pydantic import BaseModel
from typing import List

# CORREÇÃO: Importamos 'Sector' em vez de 'OrganizationSector'
from app.models.organization_model import Sector

# --- SCHEMAS DE ORGANIZAÇÃO ---

class OrganizationBase(BaseModel):
    name: str
    # CORREÇÃO: Usamos 'Sector' como o tipo esperado
    sector: Sector

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationPublic(OrganizationBase):
    id: int
    
    model_config = { "from_attributes": True }

# Este schema pode ser útil no futuro para retornar uma organização com seus utilizadores
# Para evitar erros de importação circular, vamos comentá-lo por agora.
# Se precisar dele, o ideal é usar "UpdateForwardRef" ou colocar a definição em outro local.
#
# from .user_schema import UserPublic
#
# class OrganizationWithUsers(OrganizationPublic):
#     users: List[UserPublic] = []