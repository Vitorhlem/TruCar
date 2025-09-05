from pydantic import BaseModel
from typing import Optional, List

from app.models.organization_model import Sector
from app.models.user_model import UserRole


# --- NOVO SCHEMA MÍNIMO ---
# Define apenas os campos do utilizador que precisamos DENTRO de uma organização
class UserNestedInOrganization(BaseModel):
    id: int
    role: UserRole
    
    model_config = { "from_attributes": True }


class OrganizationBase(BaseModel):
    name: str
    sector: Sector


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[Sector] = None


class OrganizationPublic(OrganizationBase):
    id: int
    # Agora usa o schema mínimo, quebrando o ciclo de importação
    users: List[UserNestedInOrganization] = []

    model_config = { "from_attributes": True }