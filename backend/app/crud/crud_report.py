from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime, timedelta
from typing import List

from app.models.vehicle_model import Vehicle, VehicleStatus
from app.models.journey_model import Journey
from app.models.organization_model import Organization
from app.models.report_models import DashboardKPIs, KmPerDay, UpcomingMaintenance


async def get_dashboard_kpis(db: AsyncSession, *, organization_id: int) -> dict:
    """Calcula os KPIs principais sobre o estado da frota e retorna como um dicionário."""
    stmt = select(Vehicle.status, func.count(Vehicle.id)).where(
        Vehicle.organization_id == organization_id
    ).group_by(Vehicle.status)
    
    result = await db.execute(stmt)
    status_counts = {status: count for status, count in result.all()}

    # Criamos o modelo Pydantic para garantir a estrutura correta dos dados
    kpis_model = DashboardKPIs(
        total_vehicles=sum(status_counts.values()),
        available_vehicles=status_counts.get(VehicleStatus.AVAILABLE.value, 0),
        in_use_vehicles=status_counts.get(VehicleStatus.IN_USE.value, 0),
        maintenance_vehicles=status_counts.get(VehicleStatus.MAINTENANCE.value, 0),
    )
    
    # --- CORREÇÃO DEFINITIVA ---
    # Devolvemos um dicionário em vez de um objeto Pydantic para evitar erros de validação aninhada.
    return kpis_model.model_dump()
    # --- FIM DA CORREÇÃO ---


async def get_km_per_day_last_30_days(db: AsyncSession, *, organization_id: int) -> List[KmPerDay]:
    """Calcula a distância/duração total por dia nos últimos 30 dias."""
    start_date = datetime.utcnow() - timedelta(days=30)
    
    org = await db.get(Organization, organization_id)
    if not org:
        return []

    if org.sector == 'agronegocio':
        distance_col = func.sum(Journey.end_engine_hours - Journey.start_engine_hours)
        filter_col = Journey.end_engine_hours.is_not(None)
    else:
        distance_col = func.sum(Journey.end_mileage - Journey.start_mileage)
        filter_col = Journey.end_mileage.is_not(None)

    stmt = (
        select(
            func.date(Journey.start_time).label("date"),
            distance_col.label("total_km")
        )
        .where(
            Journey.organization_id == organization_id,
            Journey.is_active == False,
            Journey.start_time >= start_date,
            filter_col
        )
        .group_by(func.date(Journey.start_time))
        .order_by(func.date(Journey.start_time))
    )

    result = await db.execute(stmt)
    return [KmPerDay(date=row.date, total_km=float(row.total_km or 0)) for row in result.all()]


async def get_upcoming_maintenances(db: AsyncSession, *, organization_id: int) -> List[UpcomingMaintenance]:
    """Busca veículos com manutenções futuras próximas."""
    today = datetime.utcnow().date()
    in_30_days = today + timedelta(days=30)

    stmt = (
        select(Vehicle)
        .where(
            Vehicle.organization_id == organization_id,
            or_(
                Vehicle.next_maintenance_date.between(today, in_30_days),
                (Vehicle.next_maintenance_km - Vehicle.current_km <= 1000)
            )
        )
        .order_by(Vehicle.next_maintenance_date.asc(), Vehicle.next_maintenance_km.asc())
        .limit(10)
    )
    
    result = await db.execute(stmt)
    vehicles = result.scalars().all()
    
    return [
        UpcomingMaintenance(
            vehicle_info=f"{v.brand} {v.model} ({v.license_plate or v.identifier})",
            due_date=v.next_maintenance_date,
            due_km=v.next_maintenance_km
        ) for v in vehicles
    ]

