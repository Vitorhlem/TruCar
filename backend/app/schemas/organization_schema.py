from pydantic import BaseModel
from app.models.organization_model import Sector

class OrganizationBase(BaseModel):
    name: str
    sector: Sector

# Schema para criar uma nova organização
class OrganizationCreate(OrganizationBase):
    pass

# Schema para a resposta da API
class OrganizationPublic(OrganizationBase):
    id: int
    model_config = { "from_attributes": True }