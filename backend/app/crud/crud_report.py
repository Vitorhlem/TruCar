from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, extract, or_
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta

from app import crud
from app.models.user_model import User, UserRole
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.models.journey_model import Journey
from app.models.fuel_log_model import FuelLog
from app.models.maintenance_request_model import MaintenanceRequest, MaintenanceStatus
from app.models.organization_model import Sector
# CORREÇÃO: Importamos TODAS as classes necessárias do schema
from app.schemas.report_schema import DashboardSummary, KPI, KmPerDay


async def get_driver_leaderboard(db: AsyncSession, *, organization_id: int) -> dict:
    """Calcula e retorna o ranking de performance dos motoristas de uma organização."""
    fleet_km_stmt = select(func.sum(Journey.end_mileage - Journey.start_mileage)).where(Journey.is_active == False, Journey.organization_id == organization_id)
    fleet_liters_stmt = select(func.sum(FuelLog.liters)).where(FuelLog.organization_id == organization_id)
    total_fleet_km = (await db.execute(fleet_km_stmt)).scalar_one() or 0.0
    total_fleet_liters = (await db.execute(fleet_liters_stmt)).scalar_one() or 0.0
    fleet_avg_kml = (total_fleet_km / total_fleet_liters) if total_fleet_liters > 0 else 1.0

    drivers_stmt = select(User).where(User.role == UserRole.DRIVER, User.is_active == True, User.organization_id == organization_id)
    drivers = (await db.execute(drivers_stmt)).scalars().all()

    leaderboard = []
    for driver in drivers:
        stats = await crud.user.get_user_stats(db, user_id=driver.id, organization_id=organization_id)
        
        score = 0
        if fleet_avg_kml > 0 and stats and stats.get("avg_km_per_liter", 0) > 0:
            efficiency_ratio = stats["avg_km_per_liter"] / fleet_avg_kml
            score = efficiency_ratio * 100
        
        leaderboard.append({
            "user_id": driver.id, "full_name": driver.full_name, "avatar_url": driver.avatar_url,
            "performance_score": max(0, min(score, 120)),
            "avg_km_per_liter": stats.get("avg_km_per_liter", 0) if stats else 0,
            "total_km_driven": stats.get("total_km_driven", 0) if stats else 0,
            "maintenance_requests_count": stats.get("maintenance_requests_count", 0) if stats else 0
        })

    leaderboard.sort(key=lambda x: x['performance_score'], reverse=True)
    return {"leaderboard": leaderboard}


async def get_driver_activity_data(db: AsyncSession, *, driver_id: int, organization_id: int, date_from: date, date_to: date) -> dict:
    """Agrega os dados de atividade de um motorista para um relatório em PDF, dentro de uma organização."""
    driver = await crud.user.get_user(db, user_id=driver_id, organization_id=organization_id)
    if not driver:
        raise ValueError("Motorista não encontrado nesta organização.")

    end_date = date_to + timedelta(days=1)

    journeys_stmt = select(Journey).where(
        Journey.driver_id == driver_id, Journey.organization_id == organization_id,
        Journey.start_time >= date_from, Journey.start_time < end_date, Journey.is_active == False
    ).options(selectinload(Journey.vehicle)).order_by(Journey.start_time.desc())
    journeys = (await db.execute(journeys_stmt)).scalars().all()

    fuel_logs_stmt = select(FuelLog).where(
        FuelLog.user_id == driver_id, FuelLog.organization_id == organization_id,
        FuelLog.timestamp >= date_from, FuelLog.timestamp < end_date
    ).options(selectinload(FuelLog.vehicle)).order_by(FuelLog.timestamp.desc())
    fuel_logs = (await db.execute(fuel_logs_stmt)).scalars().all()

    total_km = sum(j.end_mileage - j.start_mileage for j in journeys if j.end_mileage)
    total_fuel_cost = sum(f.total_cost for f in fuel_logs)

    return {
        "driver_name": driver.full_name, "date_from": date_from.strftime('%d/%m/%Y'),
        "date_to": date_to.strftime('%d/%m/%Y'), "year": date.today().year,
        "summary": {
            "total_journeys": len(journeys), "total_km": total_km,
            "total_fuel_cost": f"{total_fuel_cost:.2f}",
        },
        "journeys": journeys, "fuel_logs": fuel_logs,
    }


async def get_dashboard_summary(
    db: AsyncSession, *, current_user: User, start_date: datetime
) -> DashboardSummary:
    """
    Busca e agrega dados para o Dashboard. Se for um motorista,
    filtra os dados de performance para mostrar apenas a sua própria atividade.
    """
    org_id = current_user.organization_id
    sector_str = current_user.organization.sector

    # --- KPIs --- (Estes devem mostrar os totais da organização para todos)
    kpi_stmt = select(Vehicle.status, func.count(Vehicle.id)).where(Vehicle.organization_id == org_id).group_by(Vehicle.status)
    kpi_result = await db.execute(kpi_stmt)
    status_counts = {status: count for status, count in kpi_result.all()}

    # --- CÁLCULO DINÂMICO DE DISTÂNCIA / DURAÇÃO ---
    if sector_str == Sector.AGRONEGOCIO.value:
        distance_col = func.sum(Journey.end_engine_hours - Journey.start_engine_hours).label("total_distance")
        filter_col = Journey.end_engine_hours.is_not(None)
    else:
        distance_col = func.sum(Journey.end_mileage - Journey.start_mileage).label("total_distance")
        filter_col = Journey.end_mileage.is_not(None)

    # Query base para o gráfico de linha
    distance_per_day_stmt = (
        select(func.date(Journey.start_time).label("date"), distance_col)
        .where(
            Journey.organization_id == org_id,
            Journey.is_active == False,
            Journey.start_time >= start_date,
            filter_col
        )
    )
    
    # A LÓGICA INTELIGENTE QUE ESTAVA EM FALTA:
    # Se o utilizador logado for um motorista, adicionamos um filtro extra à query
    if current_user.role == UserRole.DRIVER:
        distance_per_day_stmt = distance_per_day_stmt.where(Journey.driver_id == current_user.id)
    
    # Agrupamos e ordenamos a query final
    distance_per_day_stmt = distance_per_day_stmt.group_by(func.date(Journey.start_time)).order_by(func.date(Journey.start_time))
    
    distance_result = await db.execute(distance_per_day_stmt)
    km_per_day_data = [KmPerDay(date=row.date.isoformat(), total_km=float(row.total_distance or 0)) for row in distance_result.all()]
    total_distance_or_duration = sum(item.total_km for item in km_per_day_data)

    kpis_data = KPI(
        total_vehicles=sum(status_counts.values()),
        available_vehicles=status_counts.get(VehicleStatus.AVAILABLE.value, 0),
        in_use_vehicles=status_counts.get(VehicleStatus.IN_USE.value, 0),
        maintenance_vehicles=status_counts.get(VehicleStatus.MAINTENANCE.value, 0),
        km_last_30_days=float(total_distance_or_duration),
        total_fuel_cost_current_month=0, # Placeholder
        open_maintenance_requests=0,    # Placeholder
    )
    
    active_journeys = await crud.journey.get_active_journeys(db, organization_id=org_id)

    return DashboardSummary(
        kpis=kpis_data,
        km_per_day_last_30_days=km_per_day_data,
        active_journeys=active_journeys,
        # Placeholders para as outras listas
        top_5_vehicles_by_km=[],
        fuel_cost_last_6_months=[],
        upcoming_maintenances=[],
    )