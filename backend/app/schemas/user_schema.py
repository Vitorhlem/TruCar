# backend/app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr # <-- CORREÇÃO AQUI
from typing import Optional, List

from app.models.organization_model import Sector 
from app.models.user_model import UserRole
from .organization_schema import OrganizationPublic

# --- SCHEMAS BASE DE UTILIZADOR ---

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserPublic(UserBase):
    id: int
    organization: OrganizationPublic
    role: UserRole # A role aparece na resposta

    model_config = { "from_attributes": True }

# --- SCHEMA PARA REGISTO DE NOVO UTILIZADOR/EMPRESA ---

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    organization_name: str
    sector: Sector

# --- SCHEMAS DE ESTATÍSTICAS (ADICIONADOS DE VOLTA) ---

class JourneysByVehicle(BaseModel):
    vehicle_info: str
    km_driven_in_vehicle: int

class UserStats(BaseModel):
    total_journeys: int
    total_km_driven: float
    journeys_by_vehicle: List[JourneysByVehicle]
    maintenance_requests_count: int
    avg_km_per_liter: float
    avg_cost_per_km: float
    fleet_avg_km_per_liter: float