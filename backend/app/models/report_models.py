from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- NOVO SCHEMA ADICIONADO ---
# Define a estrutura para cada motorista no mini pódio do dashboard
class DashboardPodiumDriver(BaseModel):
    full_name: str
    avatar_url: Optional[str] = None
    primary_metric_value: float

class CostByCategory(BaseModel):
    cost_type: str
    total_amount: float

class DashboardKPIs(BaseModel):
    total_vehicles: int
    available_vehicles: int
    in_use_vehicles: int
    maintenance_vehicles: int

class KmPerDay(BaseModel):
    date: date
    total_km: float

class UpcomingMaintenance(BaseModel):
    vehicle_info: str
    due_date: Optional[date] = None
    due_km: Optional[float] = None

    class Config:
        from_attributes = True