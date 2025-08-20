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
# Adicione a importação do schema para garantir a correspondência do tipo de retorno
from app.schemas.report_schema import DashboardSummary


async def get_driver_leaderboard(db: AsyncSession, *, organization_id: int) -> dict:
    """Calcula e retorna o ranking de performance dos motoristas de uma organização."""
    # ... (seu código original, sem alterações)
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
        if fleet_avg_kml > 0 and stats["avg_km_per_liter"] > 0:
            efficiency_ratio = stats["avg_km_per_liter"] / fleet_avg_kml
            score = efficiency_ratio * 100
        
        leaderboard.append({
            "user_id": driver.id, "full_name": driver.full_name, "avatar_url": driver.avatar_url,
            "performance_score": max(0, min(score, 120)), "avg_km_per_liter": stats["avg_km_per_liter"],
            "total_km_driven": stats["total_km_driven"], "maintenance_requests_count": stats["maintenance_requests_count"]
        })

    leaderboard.sort(key=lambda x: x['performance_score'], reverse=True)
    return {"leaderboard": leaderboard}


async def get_driver_activity_data(db: AsyncSession, *, driver_id: int, organization_id: int, date_from: date, date_to: date) -> dict:
    """Agrega os dados de atividade de um motorista para um relatório em PDF, dentro de uma organização."""
    # ... (seu código original, sem alterações)
    driver = await crud.user.get_user(db, user_id=driver_id)
    if not driver or driver.organization_id != organization_id:
        return {}

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

# --- FUNÇÃO CORRIGIDA ---
async def get_dashboard_summary(
    db: AsyncSession, *, current_user: User, start_date: datetime
) -> DashboardSummary:
    """
    Calcula os dados agregados para o dashboard, filtrando pela organização do utilizador.
    """
    organization_id = current_user.organization_id

    # Total de Veículos
    total_vehicles_query = select(func.count(Vehicle.id)).where(Vehicle.organization_id == organization_id)
    total_vehicles = (await db.execute(total_vehicles_query)).scalar_one_or_none() or 0

    # Veículos Disponíveis
    available_vehicles_query = select(func.count(Vehicle.id)).where(
        Vehicle.organization_id == organization_id,
        Vehicle.status == VehicleStatus.AVAILABLE
    )
    available_vehicles = (await db.execute(available_vehicles_query)).scalar_one_or_none() or 0
    
    # Total de Viagens nos últimos 30 dias
    total_journeys_query = select(func.count(Journey.id)).where(
        Journey.organization_id == organization_id,
        Journey.start_time >= start_date
    )
    total_journeys = (await db.execute(total_journeys_query)).scalar_one_or_none() or 0

    # KM Total Rodado nos últimos 30 dias - CORRIGIDO
    total_km_query = select(func.sum(Journey.end_mileage - Journey.start_mileage)).where(
        Journey.organization_id == organization_id,
        Journey.start_time >= start_date,
        Journey.end_mileage.is_not(None) # Garante que só viagens finalizadas são contadas
    )
    total_km = (await db.execute(total_km_query)).scalar_one_or_none() or 0.0

    return DashboardSummary(
        total_vehicles=total_vehicles,
        available_vehicles=available_vehicles,
        journeys_last_30_days=total_journeys,
        km_last_30_days=float(total_km), # Garante que o tipo é float
    )