from pydantic import BaseModel
from typing import Optional, List

from app.models.organization_model import Sector
from app.models.user_model import UserRole


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


class OrganizationFuelIntegrationUpdate(BaseModel):
    fuel_provider_name: Optional[str] = ""
    fuel_provider_api_key: Optional[str] = ""
    fuel_provider_api_secret: Optional[str] = ""


class OrganizationPublic(OrganizationBase):
    id: int
    users: List[UserNestedInOrganization] = []

    model_config = { "from_attributes": True }


# --- NOVO SCHEMA ADICIONADO ---
# Usado para enviar o status da configuração para o frontend de forma segura
class OrganizationFuelIntegrationPublic(BaseModel):
    fuel_provider_name: Optional[str] = None
    is_api_key_set: bool = False
    is_api_secret_set: bool = False