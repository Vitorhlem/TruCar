from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.models.report_models import KmPerDay, UpcomingMaintenance
from app.schemas.journey_schema import JourneyPublic

router = APIRouter()


# --- SCHEMAS PARA A ROTA PRINCIPAL DO DASHBOARD ---
class DashboardKPIs(BaseModel):
    total_vehicles: int
    available_vehicles: int
    in_use_vehicles: int
    maintenance_vehicles: int

class DashboardSummaryResponse(BaseModel):
    kpis: DashboardKPIs
    km_per_day_last_30_days: Optional[List[KmPerDay]] = None
    active_journeys: Optional[List[JourneyPublic]] = None
    upcoming_maintenances: Optional[List[UpcomingMaintenance]] = None

    class Config:
        from_attributes = True


# --- ROTA PRINCIPAL DO DASHBOARD ---
@router.get("/summary", response_model=DashboardSummaryResponse)
async def read_summary(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna os dados de resumo para o dashboard principal.
    Para contas CLIENTE_DEMO, os dados premium são omitidos (enviados como null).
    """
    kpis = await crud.report.get_dashboard_kpis(db, organization_id=current_user.organization_id)
    
    if current_user.role == UserRole.CLIENTE_ATIVO:
        km_per_day = await crud.report.get_km_per_day_last_30_days(db, organization_id=current_user.organization_id)
        active_journeys = await crud.journey.get_active_journeys(db, organization_id=current_user.organization_id)
        upcoming_maintenances = await crud.report.get_upcoming_maintenances(db, organization_id=current_user.organization_id)
        
        return DashboardSummaryResponse(
            kpis=kpis,
            km_per_day_last_30_days=km_per_day,
            active_journeys=active_journeys,
            upcoming_maintenances=upcoming_maintenances
        )
    else:
        # --- LÓGICA DE DEMO EXPLÍCITA ---
        # Garantimos que para qualquer outro papel (ex: CLIENTE_DEMO)
        # os campos premium são explicitamente nulos.
        return DashboardSummaryResponse(
            kpis=kpis,
            km_per_day_last_30_days=None,
            active_journeys=None,
            upcoming_maintenances=None
        )


# --- Rota de estatísticas da conta demo (para o ícone de coroa) ---
class DemoStatsResponse(BaseModel):
    vehicle_count: int
    vehicle_limit: int
    driver_count: int
    driver_limit: int
    journey_count: int
    journey_limit: int

@router.get("/demo-stats", response_model=DemoStatsResponse)
async def read_demo_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Retorna as estatísticas de uso atuais para uma organização."""
    vehicle_count = await crud.vehicle.count_by_org(db, organization_id=current_user.organization_id)
    driver_count = await crud.user.count_by_org(db, organization_id=current_user.organization_id, role=UserRole.DRIVER)
    journey_count = await crud.journey.count_journeys_in_current_month(db, organization_id=current_user.organization_id)

    return {
        "vehicle_count": vehicle_count,
        "vehicle_limit": 1,
        "driver_count": driver_count,
        "driver_limit": 2,
        "journey_count": journey_count,
        "journey_limit": 10
    }

