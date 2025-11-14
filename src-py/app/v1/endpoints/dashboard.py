from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app import crud, deps
from app.models.user_model import User, UserRole

# --- CORREÇÃO: Importar a INSTÂNCIA 'demo_usage' diretamente ---
from app.crud.crud_demo_usage import demo_usage as crud_demo_usage_instance
# -------------------------------------------------------------

# --- NOVOS IMPORTS DOS SCHEMAS CENTRALIZADOS ---
from app.schemas.dashboard_schema import (
    ManagerDashboardResponse,
    DriverDashboardResponse,
    VehiclePosition,
)

router = APIRouter()
class DemoResourceLimit(BaseModel):
    current: int
    limit: int

# --- FUNÇÃO HELPER PARA LIDAR COM O FILTRO DE PERÍODO ---
def _get_start_date_from_period(period: str) -> date:
    """Converte uma string de período ('last_7_days', etc.) em uma data de início."""
    today = datetime.utcnow().date()
    if period == "last_7_days":
        return today - timedelta(days=7)
    if period == "this_month":
        return today.replace(day=1)
    # Padrão para 'last_30_days' ou qualquer outro valor
    return today - timedelta(days=30)


# --- ENDPOINT PARA O DASHBOARD DO GESTOR ---
@router.get(
    "/manager",
    response_model=ManagerDashboardResponse,
    summary="Obtém os dados completos para o dashboard do gestor",
)
async def read_manager_dashboard(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    period: str = "last_30_days"
):
    """
    Retorna os dados agregados para o dashboard principal do gestor.
    Acessível por CLIENTE_ATIVO e CLIENTE_DEMO.
    """
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este dashboard.",
        )

    org_id = current_user.organization_id
    start_date = _get_start_date_from_period(period)

    # --- Busca de dados de custos movida para fora do 'if' ---
    costs = await crud.report.get_costs_by_category_last_30_days(db, organization_id=org_id, start_date=start_date)
    
    # --- Busca de dados comuns a todos os gestores ---
    kpis = await crud.report.get_dashboard_kpis(db, organization_id=org_id)
    efficiency_kpis = await crud.report.get_efficiency_kpis(db, organization_id=org_id, start_date=start_date)
    recent_alerts = await crud.report.get_recent_alerts(db, organization_id=org_id)
    upcoming_maintenances = await crud.report.get_upcoming_maintenances(db, organization_id=org_id)
    active_goal = await crud.report.get_active_goal_with_progress(db, organization_id=org_id)

    # --- Busca de dados premium (apenas para CLIENTE_ATIVO) ---
    if current_user.role == UserRole.CLIENTE_ATIVO:
        km_per_day = await crud.report.get_km_per_day_last_30_days(db, organization_id=org_id, start_date=start_date)
        podium = await crud.report.get_podium_drivers(db, organization_id=org_id)

        return ManagerDashboardResponse(
            kpis=kpis,
            efficiency_kpis=efficiency_kpis,
            costs_by_category=costs,
            km_per_day_last_30_days=km_per_day,
            podium_drivers=podium,
            recent_alerts=recent_alerts,
            upcoming_maintenances=upcoming_maintenances,
            active_goal=active_goal
        )
    
    # --- Resposta para CLIENTE_DEMO (sem dados premium) ---
    return ManagerDashboardResponse(
        kpis=kpis,
        efficiency_kpis=efficiency_kpis,
        costs_by_category=costs,
        recent_alerts=recent_alerts,
        upcoming_maintenances=upcoming_maintenances,
        active_goal=active_goal,
    )


# --- ENDPOINT PARA O DASHBOARD DO MOTORISTA ---
@router.get(
    "/driver",
    response_model=DriverDashboardResponse,
    summary="Obtém os dados de desempenho para o motorista logado",
)
async def read_driver_dashboard(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retorna as métricas de desempenho individuais para um motorista.
    Acessível apenas por DRIVER.
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este dashboard.",
        )

    metrics = await crud.user.get_driver_metrics(db, user=current_user)
    ranking = await crud.user.get_driver_ranking_context(db, user=current_user)
    achievements = await crud.user.get_driver_achievements(db, user=current_user)

    return DriverDashboardResponse(
        metrics=metrics,
        ranking_context=ranking,
        achievements=achievements,
    )


# --- ENDPOINT PARA O MAPA EM TEMPO REAL ---
@router.get(
    "/vehicles/positions",
    response_model=List[VehiclePosition],
    summary="Obtém a geolocalização de todos os veículos da organização",
)
async def read_vehicle_positions(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Endpoint leve, projetado para ser chamado frequentemente (polling)
    pelo frontend para atualizar o mapa em tempo real.
    """
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado.",
        )
    
    positions = await crud.report.get_vehicle_positions(db, organization_id=current_user.organization_id)
    return positions


# --- Rota de estatísticas da conta demo (MANTIDA) ---
class DemoStatsResponse(BaseModel):
    vehicles: DemoResourceLimit
    users: DemoResourceLimit
    parts: DemoResourceLimit
    clients: DemoResourceLimit
    reports: DemoResourceLimit
    fines: DemoResourceLimit
    documents: DemoResourceLimit
    freight_orders: DemoResourceLimit
    maintenance_requests: DemoResourceLimit  # CORRIGIDO: de 'maintenances'
    fuel_logs: DemoResourceLimit

@router.get("/demo-stats", response_model=DemoStatsResponse, summary="Obtém todos os limites e usos da conta demo")
async def read_demo_stats_rebuilt(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.CLIENTE_DEMO:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Esta rota é apenas para contas de demonstração.")

    org_id = current_user.organization_id
    
    # Busca contagens totais (Usando os 'alias' .count() que adicionamos)
    vehicle_count = await crud.vehicle.count(db, organization_id=org_id)
    user_count = await crud.user.count(db, organization_id=org_id)
    part_count = await crud.part.count(db, organization_id=org_id)
    client_count = await crud.client.count(db, organization_id=org_id)

    # Busca contagens mensais
    monthly_usage: Dict[str, int] = {}
    for resource_type in deps.DEMO_MONTHLY_LIMITS.keys():
        # --- CORREÇÃO: Usando a instância importada diretamente ---
        usage = await crud_demo_usage_instance.get_or_create_usage(
            db, organization_id=org_id, resource_type=resource_type
        )
        # -----------------------------------------------------
        monthly_usage[resource_type] = usage.usage_count

    return DemoStatsResponse(
        vehicles=DemoResourceLimit(current=vehicle_count, limit=deps.DEMO_TOTAL_LIMITS.get("vehicles", 0)),
        users=DemoResourceLimit(current=user_count, limit=deps.DEMO_TOTAL_LIMITS.get("users", 0)),
        parts=DemoResourceLimit(current=part_count, limit=deps.DEMO_TOTAL_LIMITS.get("parts", 0)),
        clients=DemoResourceLimit(current=client_count, limit=deps.DEMO_TOTAL_LIMITS.get("clients", 0)),
        reports=DemoResourceLimit(current=monthly_usage.get("reports", 0), limit=deps.DEMO_MONTHLY_LIMITS.get("reports", 0)),
        fines=DemoResourceLimit(current=monthly_usage.get("fines", 0), limit=deps.DEMO_MONTHLY_LIMITS.get("fines", 0)),
        documents=DemoResourceLimit(current=monthly_usage.get("documents", 0), limit=deps.DEMO_MONTHLY_LIMITS.get("documents", 0)),
        freight_orders=DemoResourceLimit(current=monthly_usage.get("freight_orders", 0), limit=deps.DEMO_MONTHLY_LIMITS.get("freight_orders", 0)),
        maintenance_requests=DemoResourceLimit(current=monthly_usage.get("maintenance_requests", 0), limit=deps.DEMO_MONTHLY_LIMITS.get("maintenance_requests", 0)), # CORRIGIDO: chave 'maintenance_requests'
        fuel_logs=DemoResourceLimit(current=monthly_usage.get("fuel_logs", 0), limit=deps.DEMO_MONTHLY_LIMITS.get("fuel_logs", 0)),
    )