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

class OrganizationNestedInUser(BaseModel):
    id: int
    name: str
    sector: Sector
    vehicle_limit: int
    driver_limit: int
    freight_order_limit: int
    maintenance_limit: int

    model_config = { "from_attributes": True }


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[Sector] = None
    vehicle_limit: Optional[int] = None
    driver_limit: Optional[int] = None
    freight_order_limit: Optional[int] = None
    maintenance_limit: Optional[int] = None


class OrganizationFuelIntegrationUpdate(BaseModel):
    fuel_provider_name: Optional[str] = ""
    fuel_provider_api_key: Optional[str] = ""
    fuel_provider_api_secret: Optional[str] = ""


class OrganizationPublic(OrganizationBase):
    id: int
    users: List[UserNestedInOrganization] = []

    vehicle_limit: int
    driver_limit: int
    freight_order_limit: int
    maintenance_limit: int

    model_config = { "from_attributes": True }


class OrganizationFuelIntegrationPublic(BaseModel):
    fuel_provider_name: Optional[str] = None
    is_api_key_set: bool = False
    is_api_secret_set: bool = False