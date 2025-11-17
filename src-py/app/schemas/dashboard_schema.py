from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.report_models import DashboardKPIs, CostByCategory, KmPerDay, DashboardPodiumDriver , UpcomingMaintenance



class KpiEfficiency(BaseModel):
    """KPIs focados em eficiência e performance financeira."""
    cost_per_km: float = Field(..., description="Custo médio por quilómetro rodado.")
    utilization_rate: float = Field(..., description="Percentagem de tempo que a frota esteve em uso.")

class VehiclePosition(BaseModel):
    """Informações de um único veículo para o mapa em tempo real."""
    id: int
    license_plate: Optional[str] = None
    identifier: Optional[str] = None
    latitude: float
    longitude: float
    status: str # Usamos str para simplicidade no frontend

    class Config:
        from_attributes = True

class AlertSummary(BaseModel):
    """Estrutura de um alerta para o widget de 'Alertas Recentes'."""
    id: int
    icon: str
    color: str
    title: str
    subtitle: str
    time: str # Formatado como string para simplicidade (ex: "2 min atrás")

class GoalStatus(BaseModel):
    """Representa o estado atual de uma meta definida."""
    title: str
    current_value: float
    target_value: float
    unit: str


class ManagerDashboardResponse(BaseModel):
    """Schema completo para a resposta do endpoint do dashboard do gestor."""
    kpis: DashboardKPIs
    efficiency_kpis: KpiEfficiency
    
    costs_by_category: Optional[List[CostByCategory]] = None
    km_per_day_last_30_days: Optional[List[KmPerDay]] = None
    podium_drivers: Optional[List[DashboardPodiumDriver]] = None
    
    recent_alerts: List[AlertSummary]
    upcoming_maintenances: List[UpcomingMaintenance]
    active_goal: Optional[GoalStatus] = None



class DriverMetrics(BaseModel):
    """Métricas de performance para um motorista individual."""
    distance: float
    hours: float
    fuel_efficiency: float
    alerts: int

class DriverRankEntry(BaseModel):
    """Entrada individual para a lista de ranking do motorista."""
    rank: int
    name: str
    metric: float
    is_current_user: bool

class AchievementStatus(BaseModel):
    """Status de uma conquista (bloqueada ou desbloqueada)."""
    title: str
    icon: str
    unlocked: bool


class DriverDashboardResponse(BaseModel):
    """Schema completo para a resposta do endpoint do dashboard do motorista."""
    metrics: DriverMetrics
    ranking_context: List[DriverRankEntry]
    achievements: List[AchievementStatus]
