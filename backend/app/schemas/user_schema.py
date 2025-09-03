from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.models.organization_model import Sector
from app.models.user_model import UserRole
from .organization_schema import OrganizationPublic

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = None
    organization_id: Optional[int] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserPublic(UserBase):
    id: int
    organization: OrganizationPublic
    role: UserRole
    is_superuser: bool # <-- CAMPO ADICIONADO

    model_config = { "from_attributes": True }

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    organization_name: str
    sector: Sector

# --- SCHEMAS DE ESTATÍSTICAS (GENÉRICOS) ---

class PerformanceByVehicle(BaseModel):
    vehicle_info: str
    value: float

class UserStats(BaseModel):
    total_journeys: int
    primary_metric_label: str
    primary_metric_value: float
    primary_metric_unit: str
    performance_by_vehicle: List[PerformanceByVehicle]
    maintenance_requests_count: int
    avg_km_per_liter: Optional[float] = None
    avg_cost_per_km: Optional[float] = None
    fleet_avg_km_per_liter: Optional[float] = None

# --- SCHEMAS DE PLACAR DE LÍDERES ---

class LeaderboardUser(BaseModel):
    # O conteúdo desta classe PRECISA estar indentado
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    primary_metric_value: float
    total_journeys: int

    model_config = { "from_attributes": True }

class LeaderboardResponse(BaseModel):
    # O conteúdo desta classe PRECISA estar indentado
    leaderboard: List[LeaderboardUser]
    primary_metric_unit: str