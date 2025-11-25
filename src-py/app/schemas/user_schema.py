from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.models.organization_model import Sector
from app.models.user_model import UserRole
from .organization_schema import OrganizationPublic

class OrganizationNestedInUser(BaseModel):
    id: int
    name: str
    sector: Sector
    vehicle_limit: int
    driver_limit: int
    model_config = { "from_attributes": True }

class UserBase(BaseModel):
    email: str
    full_name: str
    is_active: bool = True
    avatar_url: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = None
    organization_id: Optional[int] = None
    email: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None # <--- Adicionado aqui
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    notify_in_app: Optional[bool] = None
    notify_by_email: Optional[bool] = None
    notification_email: Optional[str] = None
    employee_id: Optional[str] = None # Permite a edição do ID se necessário
    avatar_url: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserNotificationPrefsUpdate(BaseModel):
    notify_in_app: bool
    notify_by_email: bool
    notification_email: Optional[str] = None

class UserPublic(UserBase):
    id: int
    organization: Optional[OrganizationNestedInUser] = None
    role: UserRole
    is_superuser: bool
    notify_in_app: bool
    notify_by_email: bool
    notification_email: Optional[str] = None
    
    # --- CAMPO ADICIONADO PARA EXIBIÇÃO ---
    employee_id: Optional[str] = None
    # --- FIM DA ADIÇÃO ---

    model_config = { "from_attributes": True }

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    organization_name: str
    sector: Sector

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

class LeaderboardUser(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    primary_metric_value: float
    total_journeys: int
    model_config = { "from_attributes": True }

class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardUser]
    primary_metric_unit: str

