from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from sqlalchemy import select, func, desc
from app import crud, deps
from app.models.alert_model import Alert
from sqlalchemy.orm import selectinload
from app.models.journey_model import Journey
from app.models.user_model import User, UserRole
from app.models.fuel_log_model import FuelLog
# --- CORREÇÃO: Importar a INSTÂNCIA 'demo_usage' diretamente ---
from app.crud.crud_demo_usage import demo_usage as crud_demo_usage_instance
# -------------------------------------------------------------
from app.core.config import settings
# --- NOVOS IMPORTS DOS SCHEMAS CENTRALIZADOS ---
from app.schemas.dashboard_schema import (
    ManagerDashboardResponse, 
    DriverDashboardResponse, 
    DriverMetrics, 
    DriverRankEntry, 
    AchievementStatus,
    VehiclePosition,
    ActiveJourneyInfo # <--- NOVO SCHEMA
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
    Acessível por CLIENTE_ATIVO, CLIENTE_DEMO e ADMIN.
    """
    # --- CORREÇÃO: Adicionado UserRole.ADMIN na lista de permissões ---
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este dashboard.",
        )

    org_id = current_user.organization_id
    start_date = _get_start_date_from_period(period)

    # --- Busca de dados de custos ---
    costs = await crud.report.get_costs_by_category_last_30_days(db, organization_id=org_id, start_date=start_date)
    
    # --- Busca de dados comuns a todos os gestores ---
    kpis = await crud.report.get_dashboard_kpis(db, organization_id=org_id)
    efficiency_kpis = await crud.report.get_efficiency_kpis(db, organization_id=org_id, start_date=start_date)
    recent_alerts = await crud.report.get_recent_alerts(db, organization_id=org_id)
    upcoming_maintenances = await crud.report.get_upcoming_maintenances(db, organization_id=org_id)
    active_goal = await crud.report.get_active_goal_with_progress(db, organization_id=org_id)

    # --- Busca de dados premium (CLIENTE_ATIVO ou ADMIN) ---
    # O Admin vê tudo o que o Cliente Ativo vê.
    if current_user.role in [UserRole.CLIENTE_ATIVO, UserRole.ADMIN]:
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
@router.get("/driver", response_model=DriverDashboardResponse)
async def read_driver_dashboard(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user), # Permite 'driver'
):
    """Retorna os dados do cockpit do motorista."""
    
    # Definir período (Últimos 30 dias)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    # 1. BUSCAR JORNADA ATIVA (Correção do "Não possui operação")
    active_journey_stmt = select(Journey).where(
        Journey.driver_id == current_user.id,
        Journey.is_active == True
    ).options(selectinload(Journey.vehicle))
    
    active_journey_db = (await db.execute(active_journey_stmt)).scalars().first()
    
    active_journey_data = None
    if active_journey_db:
        # Determina data de início (pode vir como string ou datetime dependendo do driver do banco)
        start_time_val = active_journey_db.start_time
        
        active_journey_data = ActiveJourneyInfo(
            id=active_journey_db.id,
            vehicle_identifier=f"{active_journey_db.vehicle.brand} {active_journey_db.vehicle.model}",
            start_time=start_time_val if isinstance(start_time_val, datetime) else datetime.fromisoformat(str(start_time_val)),
            current_km_or_hour=active_journey_db.vehicle.current_km if active_journey_db.vehicle.current_km else (active_journey_db.vehicle.current_engine_hours or 0)
        )

    # 2. CALCULAR MÉTRICAS (Correção do FuelLog e Agregação)
    
    # Distância / Horas (Soma de jornadas finalizadas no período)
    journeys_metrics_stmt = select(
        func.sum(func.coalesce(Journey.end_mileage, 0) - func.coalesce(Journey.start_mileage, 0)), # Distância (KM)
        func.sum(func.coalesce(Journey.end_engine_hours, 0) - func.coalesce(Journey.start_engine_hours, 0)) # Horas (Motor)
    ).where(
        Journey.driver_id == current_user.id,
        Journey.is_active == False,
        Journey.end_time >= start_date
    )
    j_res = (await db.execute(journeys_metrics_stmt)).first()
    
    total_distance = float(j_res[0] or 0)
    total_hours = float(j_res[1] or 0)

    # Combustível (Corrigido: usa .timestamp e não .date)
    fuel_metrics_stmt = select(
        func.sum(FuelLog.liters)
    ).where(
        FuelLog.user_id == current_user.id,
        FuelLog.timestamp >= start_date
    )
    total_liters = (await db.execute(fuel_metrics_stmt)).scalar_one_or_none() or 0.0

    # Alertas
    alerts_count = (await db.execute(
        select(func.count(Alert.id)).where(Alert.driver_id == current_user.id, Alert.timestamp >= start_date)
    )).scalar_one()

    # Eficiência
    efficiency = 0.0
    if total_liters > 0:
        # Lógica inteligente: Se rodou mais horas que km (Agro), usa L/h. Se não, Km/l.
        if total_hours > total_distance and total_hours > 0:
             efficiency = total_liters / total_hours # L/h (Consumo)
        elif total_distance > 0:
             efficiency = total_distance / total_liters # Km/l (Rendimento)

    metrics = DriverMetrics(
        distance=total_distance,
        hours=total_hours,
        fuel_efficiency=efficiency,
        alerts=alerts_count
    )

    # 3. RANKING (Simplificado)
    ranking = [
        DriverRankEntry(rank=1, name=current_user.full_name, metric=total_distance, is_current_user=True)
    ]

    # 4. CONQUISTAS (Simplificado)
    achievements = [
        AchievementStatus(title="Primeira Viagem", icon="flag", unlocked=total_distance > 0),
        AchievementStatus(title="Motorista Seguro", icon="shield", unlocked=alerts_count == 0),
        AchievementStatus(title="Maratona 1000km", icon="speed", unlocked=total_distance > 1000),
    ]

    return DriverDashboardResponse(
        metrics=metrics,
        active_journey=active_journey_data, 
        ranking_context=ranking,
        achievements=achievements
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
    # --- CORREÇÃO: Adicionado UserRole.ADMIN ---
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO, UserRole.ADMIN]:
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
    
    vehicle_count = await crud.vehicle.count(db, organization_id=org_id)
    user_count = await crud.user.count(db, organization_id=org_id)
    part_count = await crud.part.count(db, organization_id=org_id)
    client_count = await crud.client.count(db, organization_id=org_id)

    monthly_usage: Dict[str, int] = {}
    # --- CORREÇÃO 2: Usar settings.DEMO_MONTHLY_LIMITS ---
    for resource_type in settings.DEMO_MONTHLY_LIMITS.keys():
        usage = await crud_demo_usage_instance.get_or_create_usage(
            db, organization_id=org_id, resource_type=resource_type
        )
        monthly_usage[resource_type] = usage.usage_count

    # --- CORREÇÃO 3: Usar settings em todo o retorno ---
    return DemoStatsResponse(
        vehicles=DemoResourceLimit(current=vehicle_count, limit=settings.DEMO_TOTAL_LIMITS.get("vehicles", 0)),
        users=DemoResourceLimit(current=user_count, limit=settings.DEMO_TOTAL_LIMITS.get("users", 0)),
        parts=DemoResourceLimit(current=part_count, limit=settings.DEMO_TOTAL_LIMITS.get("parts", 0)),
        clients=DemoResourceLimit(current=client_count, limit=settings.DEMO_TOTAL_LIMITS.get("clients", 0)),
        reports=DemoResourceLimit(current=monthly_usage.get("reports", 0), limit=settings.DEMO_MONTHLY_LIMITS.get("reports", 0)),
        fines=DemoResourceLimit(current=monthly_usage.get("fines", 0), limit=settings.DEMO_MONTHLY_LIMITS.get("fines", 0)),
        documents=DemoResourceLimit(current=monthly_usage.get("documents", 0), limit=settings.DEMO_MONTHLY_LIMITS.get("documents", 0)),
        freight_orders=DemoResourceLimit(current=monthly_usage.get("freight_orders", 0), limit=settings.DEMO_MONTHLY_LIMITS.get("freight_orders", 0)),
        maintenance_requests=DemoResourceLimit(current=monthly_usage.get("maintenance_requests", 0), limit=settings.DEMO_MONTHLY_LIMITS.get("maintenance_requests", 0)),
        fuel_logs=DemoResourceLimit(current=monthly_usage.get("fuel_logs", 0), limit=settings.DEMO_MONTHLY_LIMITS.get("fuel_logs", 0)),
    )