from pydantic import BaseModel
from app.models.organization_model import Sector

class OrganizationBase(BaseModel):
    name: str
    sector: Sector

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationPublic(OrganizationBase):
    id: int
    model_config = { "from_attributes": True }