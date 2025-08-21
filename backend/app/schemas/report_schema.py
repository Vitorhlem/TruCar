from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from app.schemas.journey_schema import JourneyPublic

class KPI(BaseModel):
    total_vehicles: int
    available_vehicles: int
    in_use_vehicles: int
    maintenance_vehicles: int
    total_fuel_cost_current_month: float
    open_maintenance_requests: int
    km_last_30_days: float # Este campo será usado para KM ou Horas


class KmPerDay(BaseModel):
    date: str
    total_km: float

class TopVehicle(BaseModel):
    vehicle_info: str
    total_km: int

class FuelCostPerMonth(BaseModel):
    month: str # Formato "YYYY-MM"
    total_cost: float

class UpcomingMaintenance(BaseModel):
    vehicle_info: str
    due_date: Optional[date] = None
    due_km: Optional[int] = None

class DashboardSummary(BaseModel):
    kpis: KPI
    km_per_day_last_30_days: List[KmPerDay]
    top_5_vehicles_by_km: List[TopVehicle]
    fuel_cost_last_6_months: List[FuelCostPerMonth]
    upcoming_maintenances: List[UpcomingMaintenance]
    active_journeys: List[JourneyPublic]