from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import selectinload
from app.models.inventory_transaction_model import InventoryTransaction
from app import crud
# --- IMPORTS DE MODELS ---
from app.models.user_model import User, UserRole
from app.models.alert_model import Alert, AlertLevel
from app.models.goal_model import Goal
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.models.journey_model import Journey
from app.models.organization_model import Organization
from app.models.report_models import DashboardKPIs, KmPerDay, UpcomingMaintenance, CostByCategory, DashboardPodiumDriver
from app.models.vehicle_cost_model import VehicleCost
from app.models.fuel_log_model import FuelLog
from app.models.maintenance_model import MaintenanceRequest, MaintenancePartChange, MaintenanceComment, MaintenanceStatus
from app.models.vehicle_component_model import VehicleComponent
from app.models.part_model import Part
from app.models.fine_model import Fine
from app.models.document_model import Document
from app.models.tire_model import VehicleTire as Tire

# --- IMPORTS DE SCHEMAS ---
from app.schemas.dashboard_schema import KpiEfficiency, AlertSummary, GoalStatus, VehiclePosition
from app.schemas.report_schema import (
    DashboardSummary,
    FleetManagementReport, 
    VehicleRankingEntry, 
    FleetReportSummary, 
    DriverPerformanceEntry, 
    VehicleConsolidatedReport, 
    VehicleReportPerformanceSummary, 
    VehicleReportFinancialSummary, 
    DriverPerformanceReport,
    VehicleReportSections
)

# --- FUNÇÃO HELPER ---
async def get_fleet_management_data(
    db: AsyncSession, *, start_date: date, end_date: date, organization_id: int
) -> FleetManagementReport:
    """
    Agrega dados de custo e performance de toda a frota para um período.
    """
    # 1. Obter todos os veículos da organização
    vehicles_stmt = select(Vehicle).where(Vehicle.organization_id == organization_id)
    vehicles = (await db.execute(vehicles_stmt)).scalars().all()
    
    vehicle_ids = [v.id for v in vehicles]

    # 2. Obter todos os custos e abastecimentos do período
    costs_stmt = select(VehicleCost).where(
        VehicleCost.organization_id == organization_id,
        VehicleCost.date.between(start_date, end_date)
    )
    fuel_logs_stmt = select(FuelLog).where(
        FuelLog.organization_id == organization_id,
        func.date(FuelLog.timestamp).between(start_date, end_date)
    )
    
    all_costs = (await db.execute(costs_stmt)).scalars().all()
    all_fuel_logs = (await db.execute(fuel_logs_stmt)).scalars().all()

    # 3. Calcular Resumos
    total_fleet_cost = sum(c.amount for c in all_costs)
    
    costs_by_category: Dict[str, float] = {}
    for cost in all_costs:
        category_key = str(cost.cost_type.value)
        costs_by_category[category_key] = costs_by_category.get(category_key, 0) + cost.amount

    # 4. Processar dados por veículo
    vehicle_metrics: List[Dict] = []
    total_fleet_distance = 0.0

    for vehicle in vehicles:
        costs = [c for c in all_costs if c.vehicle_id == vehicle.id]
        fuel_logs = [f for f in all_fuel_logs if f.vehicle_id == vehicle.id]
        
        total_cost = sum(c.amount for c in costs)
        
        distance = 0.0
        if len(fuel_logs) > 1:
            sorted_logs = sorted(fuel_logs, key=lambda log: log.odometer or 0)
            min_odo = sorted_logs[0].odometer or 0
            max_odo = sorted_logs[-1].odometer or 0
            distance = float(max_odo - min_odo)
        
        total_fleet_distance += distance
        
        total_liters = sum(log.liters for log in fuel_logs if log.liters)
        avg_consumption = (distance / total_liters) if total_liters > 0 else 0
        cost_per_km = (total_cost / distance) if distance > 0 else 0

        vehicle_metrics.append({
            "id": vehicle.id,
            "identifier": vehicle.license_plate or vehicle.identifier,
            "total_cost": total_cost,
            "cost_per_km": cost_per_km,
            "avg_consumption": avg_consumption
        })

    # 5. Rankings
    top_expensive = sorted(vehicle_metrics, key=lambda v: v.get('total_cost', 0), reverse=True)[:5]
    top_cost_per_km = sorted(vehicle_metrics, key=lambda v: v.get('cost_per_km', 0), reverse=True)[:5]
    top_efficient = sorted(vehicle_metrics, key=lambda v: v.get('avg_consumption', 0), reverse=True)[:5]
    least_efficient = sorted([v for v in vehicle_metrics if v.get('avg_consumption', 0) > 0], key=lambda v: v.get('avg_consumption', 0))[:5]

    summary = FleetReportSummary(
        total_cost=total_fleet_cost,
        total_distance_km=total_fleet_distance,
        overall_cost_per_km=(total_fleet_cost / total_fleet_distance) if total_fleet_distance > 0 else 0
    )

    report_data = FleetManagementReport(
        report_period_start=start_date,
        report_period_end=end_date,
        generated_at=datetime.utcnow(),
        summary=summary,
        costs_by_category=costs_by_category,
        top_5_most_expensive_vehicles=[VehicleRankingEntry(vehicle_id=v['id'], vehicle_identifier=v['identifier'], value=v['total_cost'], unit='R$') for v in top_expensive],
        top_5_highest_cost_per_km_vehicles=[VehicleRankingEntry(vehicle_id=v['id'], vehicle_identifier=v['identifier'], value=v['cost_per_km'], unit='R$/km') for v in top_cost_per_km],
        top_5_most_efficient_vehicles=[VehicleRankingEntry(vehicle_id=v['id'], vehicle_identifier=v['identifier'], value=v['avg_consumption'], unit='km/l') for v in top_efficient],
        top_5_least_efficient_vehicles=[VehicleRankingEntry(vehicle_id=v['id'], vehicle_identifier=v['identifier'], value=v['avg_consumption'], unit='km/l') for v in least_efficient]
    )
    
    return report_data

def _format_relative_time(dt: datetime) -> str:
    now = datetime.utcnow()
    delta = now - dt
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return "agora mesmo"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"há {minutes} minuto{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"há {hours} hora{'s' if hours > 1 else ''}"
    else:
        days = int(seconds / 86400)
        return f"há {days} dia{'s' if days > 1 else ''}"

# --- FUNÇÕES DE DASHBOARD ---

async def get_dashboard_kpis(db: AsyncSession, *, organization_id: int) -> dict:
    stmt = select(Vehicle.status, func.count(Vehicle.id)).where(
        Vehicle.organization_id == organization_id
    ).group_by(Vehicle.status)
    
    result = await db.execute(stmt)
    status_counts = {status: count for status, count in result.all()}

    maintenance_stmt = select(func.count(func.distinct(MaintenanceRequest.vehicle_id))).where(
        MaintenanceRequest.organization_id == organization_id,
        MaintenanceRequest.status.notin_([MaintenanceStatus.CONCLUIDA, MaintenanceStatus.REJEITADA])
    )
    active_maintenance_count = (await db.execute(maintenance_stmt)).scalar_one_or_none() or 0

    kpis_model = DashboardKPIs(
        total_vehicles=sum(status_counts.values()),
        available_vehicles=status_counts.get(VehicleStatus.AVAILABLE.value, 0),
        in_use_vehicles=status_counts.get(VehicleStatus.IN_USE.value, 0),
        maintenance_vehicles=active_maintenance_count,
    )
    return kpis_model.model_dump()


async def get_costs_by_category_last_30_days(db: AsyncSession, *, organization_id: int, start_date: date | None = None) -> List[CostByCategory]:
    if not start_date:
        start_date = datetime.utcnow().date() - timedelta(days=30)
    
    stmt = (
        select(
            VehicleCost.cost_type,
            func.sum(VehicleCost.amount).label("total_amount")
        )
        .where(
            VehicleCost.organization_id == organization_id,
            VehicleCost.date >= start_date
        )
        .group_by(VehicleCost.cost_type)
        .order_by(func.sum(VehicleCost.amount).desc())
    )
    
    result = await db.execute(stmt)
    return [CostByCategory(cost_type=row.cost_type.value, total_amount=float(row.total_amount or 0)) for row in result.all()]


# --- CORREÇÃO PRINCIPAL: Instanciação Manual do Modelo ---
async def get_podium_drivers(db: AsyncSession, *, organization_id: int) -> List[DashboardPodiumDriver]:
    leaderboard_data = await crud.user.get_leaderboard_data(db, organization_id=organization_id)
    top_drivers_raw = leaderboard_data.get("leaderboard", [])[:3]
    
    # Aqui convertemos manualmente as Linhas (Rows) do SQLAlchemy para o Objeto Pydantic
    # Isso resolve o erro "Input should be a valid dictionary..."
    result = []
    for row in top_drivers_raw:
        driver = DashboardPodiumDriver(
            full_name=row.full_name,
            avatar_url=row.avatar_url,
            primary_metric_value=float(row.primary_metric_value or 0.0)
        )
        result.append(driver)
        
    return result
# ---------------------------------------------------------


async def get_km_per_day_last_30_days(db: AsyncSession, *, organization_id: int, start_date: date | None = None) -> List[KmPerDay]:
    if not start_date:
        start_date = datetime.utcnow().date() - timedelta(days=30)
        
    org = await db.get(Organization, organization_id)
    if not org: return []

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
            func.date(Journey.start_time) >= start_date,
            filter_col
        )
        .group_by(func.date(Journey.start_time))
        .order_by(func.date(Journey.start_time))
    )

    result = await db.execute(stmt)
    return [KmPerDay(date=row.date, total_km=float(row.total_km or 0)) for row in result.all()]


async def get_upcoming_maintenances(db: AsyncSession, *, organization_id: int) -> List[UpcomingMaintenance]:
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
            vehicle_id=v.id,
            vehicle_info=f"{v.brand} {v.model} ({v.license_plate or v.identifier})",
            due_date=v.next_maintenance_date,
            due_km=v.next_maintenance_km
        ) for v in vehicles
    ]

# --- DASHBOARD AVANÇADO ---

async def get_efficiency_kpis(db: AsyncSession, *, organization_id: int, start_date: date) -> KpiEfficiency:
    costs_stmt = select(func.sum(VehicleCost.amount)).where(
        VehicleCost.organization_id == organization_id,
        VehicleCost.date >= start_date
    )
    total_costs = (await db.execute(costs_stmt)).scalar_one_or_none() or 0

    km_data = await get_km_per_day_last_30_days(db, organization_id=organization_id, start_date=start_date)
    total_km = sum(item.total_km for item in km_data)
    
    cost_per_km = (total_costs / total_km) if total_km > 0 else 0

    total_vehicles_stmt = select(func.count(Vehicle.id)).where(Vehicle.organization_id == organization_id)
    total_vehicles = (await db.execute(total_vehicles_stmt)).scalar_one()

    in_use_vehicles_stmt = select(func.count(Vehicle.id)).where(
        Vehicle.organization_id == organization_id,
        Vehicle.status == VehicleStatus.IN_USE
    )
    in_use_vehicles = (await db.execute(in_use_vehicles_stmt)).scalar_one()

    utilization_rate = (in_use_vehicles / total_vehicles) * 100 if total_vehicles > 0 else 0

    return KpiEfficiency(cost_per_km=cost_per_km, utilization_rate=utilization_rate)


async def get_recent_alerts(db: AsyncSession, *, organization_id: int) -> List[AlertSummary]:
    stmt = (
        select(Alert, Vehicle.license_plate, Vehicle.identifier, User.full_name)
        .outerjoin(Vehicle, Alert.vehicle_id == Vehicle.id)
        .outerjoin(User, Alert.driver_id == User.id)
        .where(Alert.organization_id == organization_id)
        .order_by(Alert.timestamp.desc())
        .limit(5)
    )
    result = await db.execute(stmt)
    alerts = []
    for row in result.all():
        alert, license_plate, identifier, full_name = row
        
        subtitle = f"Veículo: {license_plate or identifier or 'N/A'}"
        if full_name:
            subtitle += f" | Motorista: {full_name}"

        alerts.append(AlertSummary(
            id=alert.id,
            icon="warning" if alert.level != AlertLevel.INFO else "info",
            color="negative" if alert.level == AlertLevel.CRITICAL else ("warning" if alert.level == AlertLevel.WARNING else "info"),
            title=alert.message,
            subtitle=subtitle,
            time=_format_relative_time(alert.timestamp)
        ))
    return alerts


async def get_active_goal_with_progress(db: AsyncSession, *, organization_id: int) -> Optional[GoalStatus]:
    today = datetime.utcnow().date()
    stmt = select(Goal).where(
        Goal.organization_id == organization_id,
        Goal.period_start <= today,
        Goal.period_end >= today
    ).order_by(Goal.id.desc())
    
    active_goal = (await db.execute(stmt)).scalars().first()
    if not active_goal:
        return None

    current_value = 0
    if active_goal.unit == "R$":
        costs_stmt = select(func.sum(VehicleCost.amount)).where(
            VehicleCost.organization_id == organization_id,
            VehicleCost.date.between(active_goal.period_start, active_goal.period_end)
        )
        current_value = (await db.execute(costs_stmt)).scalar_one_or_none() or 0

    return GoalStatus(
        title=active_goal.title,
        current_value=current_value,
        target_value=active_goal.target_value,
        unit=active_goal.unit
    )


async def get_vehicle_positions(db: AsyncSession, *, organization_id: int) -> List[VehiclePosition]:
    stmt = select(Vehicle).where(
        Vehicle.organization_id == organization_id,
        Vehicle.last_latitude.is_not(None),
        Vehicle.last_longitude.is_not(None),
    )
    result = await db.execute(stmt)
    vehicles = result.scalars().all()
    return [VehiclePosition.from_orm(v) for v in vehicles]
    

# --- FUNÇÃO PRINCIPAL (RELATÓRIO CONSOLIDADO) ---
async def get_vehicle_consolidated_data(
    db: AsyncSession,
    vehicle_id: int,
    start_date: date,
    end_date: date,
    sections: VehicleReportSections,
    organization_id: int
) -> VehicleConsolidatedReport:
    
    # 1. Buscar Veículo
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle or vehicle.organization_id != organization_id:
        raise ValueError("Veículo não encontrado ou não pertence à organização.")

    # 2. Buscar Organização para lógica de setor
    org = await db.get(Organization, organization_id)
    if not org:
        raise ValueError("Organização não encontrada.")

    # 3. Buscar Dados Condicionais
    costs_data = []
    if sections.costs_detailed or sections.financial_summary:
        costs_stmt = select(VehicleCost).where(
            VehicleCost.vehicle_id == vehicle_id,
            VehicleCost.date.between(start_date, end_date)
        )
        costs_data = (await db.execute(costs_stmt)).scalars().all()

    fuel_logs_data = []
    if sections.fuel_logs_detailed or sections.performance_summary:
        fuel_logs_stmt = select(FuelLog).where(
            FuelLog.vehicle_id == vehicle_id,
            func.date(FuelLog.timestamp).between(start_date, end_date)
        )
        fuel_logs_data = (await db.execute(fuel_logs_stmt)).scalars().all()
        
    maintenance_data = []
    if sections.maintenance_detailed:
        maintenance_stmt = select(MaintenanceRequest).where(
            MaintenanceRequest.vehicle_id == vehicle_id,
            func.date(MaintenanceRequest.created_at).between(start_date, end_date)
        ).options(
            selectinload(MaintenanceRequest.comments).selectinload(MaintenanceComment.user),
            selectinload(MaintenanceRequest.services),
            selectinload(MaintenanceRequest.reporter),
            selectinload(MaintenanceRequest.approver),
            selectinload(MaintenanceRequest.part_changes).options(
                selectinload(MaintenancePartChange.user),
                selectinload(MaintenancePartChange.component_removed).options(
                    selectinload(VehicleComponent.part).selectinload(Part.items),
                    selectinload(VehicleComponent.inventory_transaction).selectinload(InventoryTransaction.item)
                ),
                selectinload(MaintenancePartChange.component_installed).options(
                    selectinload(VehicleComponent.part).selectinload(Part.items),
                    selectinload(VehicleComponent.inventory_transaction).selectinload(InventoryTransaction.item)
                )
            )
        )
        maintenance_data = (await db.execute(maintenance_stmt)).scalars().unique().all()

    fines_data = []
    if sections.fines_detailed:
        fines_stmt = select(Fine).where(
            Fine.vehicle_id == vehicle_id,
            Fine.date.between(start_date, end_date)
        ).options(selectinload(Fine.driver))
        fines_data = (await db.execute(fines_stmt)).scalars().unique().all()

    journeys_data = []
    if sections.journeys_detailed or sections.performance_summary or sections.financial_summary:
        journeys_stmt = select(Journey).where(
            Journey.vehicle_id == vehicle_id,
            func.date(Journey.start_time).between(start_date, end_date),
            Journey.is_active == False
        )
        journeys_data = (await db.execute(journeys_stmt)).scalars().all()
        
    documents_data = []
    if sections.documents_detailed:
        docs_stmt = select(Document).where(
            Document.vehicle_id == vehicle_id,
            Document.organization_id == organization_id
        )
        documents_data = (await db.execute(docs_stmt)).scalars().all()

    tires_data = []
    if sections.tires_detailed:
        tires_stmt = select(Tire).where(
            Tire.vehicle_id == vehicle_id
        )
        tires_data = (await db.execute(tires_stmt)).scalars().all()

    # --- 4. CALCULAR MÉTRICAS ---
    
    period_total_activity = 0.0
    vehicle_total_activity = 0.0
    activity_unit = "km" 

    if org.sector == 'agronegocio':
        activity_unit = "horas"
        vehicle_total_activity = vehicle.current_engine_hours or 0.0
        for j in journeys_data:
            if j.end_engine_hours and j.start_engine_hours and j.end_engine_hours > j.start_engine_hours:
                period_total_activity += (j.end_engine_hours - j.start_engine_hours)
    else: 
        activity_unit = "km"
        vehicle_total_activity = vehicle.current_km or 0.0
        for j in journeys_data:
            if j.end_mileage and j.start_mileage and j.end_mileage > j.start_mileage:
                period_total_activity += (j.end_mileage - j.start_mileage)

    # --- 5. ATUALIZAR SUMÁRIOS ---
    
    performance_summary = None
    if sections.performance_summary:
        period_total_fuel = sum(log.liters for log in fuel_logs_data if log.liters)
        avg_consumption = 0.0
        if period_total_fuel > 0:
            if activity_unit == 'km':
                avg_consumption = period_total_activity / period_total_fuel if period_total_activity > 0 else 0
            else:
                avg_consumption = period_total_fuel / period_total_activity if period_total_activity > 0 else 0
        
        performance_summary = VehicleReportPerformanceSummary(
            vehicle_total_activity=vehicle_total_activity,
            period_total_activity=period_total_activity,
            activity_unit=activity_unit,
            period_total_fuel=period_total_fuel,
            average_consumption=avg_consumption
        )

    financial_summary = None
    if sections.financial_summary:
        total_costs = sum(cost.amount for cost in costs_data)
        cost_per_metric = (total_costs / period_total_activity) if period_total_activity > 0 else 0.0
        
        costs_by_category = {}
        for cost in costs_data:
            costs_by_category[cost.cost_type.value] = costs_by_category.get(cost.cost_type.value, 0.0) + cost.amount
            
        financial_summary = VehicleReportFinancialSummary(
            total_costs=total_costs,
            cost_per_metric=cost_per_metric,
            metric_unit=activity_unit,
            costs_by_category=costs_by_category
        )

    # --- 6. MONTAGEM FINAL ---
    return VehicleConsolidatedReport(
        vehicle_id=vehicle.id,
        vehicle_identifier=vehicle.license_plate or vehicle.identifier,
        vehicle_model=f"{vehicle.brand} {vehicle.model}",
        report_period_start=start_date,
        report_period_end=end_date,
        generated_at=datetime.utcnow(),
        
        performance_summary=performance_summary,
        financial_summary=financial_summary,
        
        costs_detailed=costs_data if sections.costs_detailed else None,
        fuel_logs_detailed=fuel_logs_data if sections.fuel_logs_detailed else None,
        maintenance_detailed=maintenance_data if sections.maintenance_detailed else None,
        fines_detailed=fines_data if sections.fines_detailed else None,
        journeys_detailed=journeys_data if sections.journeys_detailed else None,
        documents_detailed=documents_data if sections.documents_detailed else None,
        tires_detailed=tires_data if sections.tires_detailed else None
    )


async def get_driver_performance_data(
    db: AsyncSession, *, start_date: date, end_date: date, organization_id: int
) -> DriverPerformanceReport:
    """
    Busca e agrega dados de desempenho para todos os motoristas de uma organização
    em um período específico.
    """
    drivers_stmt = select(User).where(
        User.organization_id == organization_id, 
        User.role == 'driver'
    )
    drivers = (await db.execute(drivers_stmt)).scalars().all()

    drivers_performance_data: List[DriverPerformanceEntry] = []

    for driver in drivers:
        journeys_stmt = select(func.count(Journey.id), func.sum(Journey.distance_km)).where(
            Journey.driver_id == driver.id,
            func.date(Journey.start_time).between(start_date, end_date)
        )
        journey_metrics = (await db.execute(journeys_stmt)).first()
        total_journeys = journey_metrics[0] or 0
        total_distance = float(journey_metrics[1] or 0.0)

        fuel_stmt = select(func.sum(FuelLog.liters), func.sum(FuelLog.total_cost)).where(
            FuelLog.user_id == driver.id,
            func.date(FuelLog.timestamp).between(start_date, end_date)
        )
        fuel_metrics = (await db.execute(fuel_stmt)).first()
        total_liters = float(fuel_metrics[0] or 0.0)
        total_fuel_cost = float(fuel_metrics[1] or 0.0)

        maintenance_stmt = select(func.count(MaintenanceRequest.id)).where(
            MaintenanceRequest.reported_by_id == driver.id,
            func.date(MaintenanceRequest.created_at).between(start_date, end_date)
        )
        maintenance_count = (await db.execute(maintenance_stmt)).scalar_one_or_none() or 0
        
        avg_consumption = (total_distance / total_liters) if total_liters > 0 else 0
        cost_per_km = (total_fuel_cost / total_distance) if total_distance > 0 else 0

        drivers_performance_data.append(
            DriverPerformanceEntry(
                driver_id=driver.id,
                driver_name=driver.full_name,
                total_journeys=total_journeys,
                total_distance_km=total_distance,
                total_fuel_liters=total_liters,
                average_consumption=avg_consumption,
                total_fuel_cost=total_fuel_cost,
                cost_per_km=cost_per_km,
                maintenance_requests=maintenance_count,
            )
        )

    sorted_performance_data = sorted(drivers_performance_data, key=lambda d: d.cost_per_km, reverse=True)

    report_data = DriverPerformanceReport(
        report_period_start=start_date,
        report_period_end=end_date,
        generated_at=datetime.utcnow(),
        drivers_performance=sorted_performance_data
    )

    return report_data

async def get_driver_activity_data(db: AsyncSession, driver_id: int, organization_id: int, date_from: date, date_to: date) -> Dict[str, Any]:
    driver = await crud.user.get(db, id=driver_id)
    if not driver or driver.organization_id != organization_id:
        raise ValueError("Motorista não encontrado")
    
    journeys_stmt = select(Journey).where(
        Journey.driver_id == driver_id,
        func.date(Journey.start_time).between(date_from, date_to)
    ).order_by(Journey.start_time.desc())
    
    journeys = (await db.execute(journeys_stmt)).scalars().all()
    
    return {
        "driver_name": driver.full_name,
        "period": f"{date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}",
        "journeys": journeys
    }


async def get_dashboard_summary(self, db: AsyncSession, current_user: User, start_date: datetime) -> DashboardSummary:
    try:
        total_vehicles_q = select(func.count(Vehicle.id)).where(Vehicle.organization_id == current_user.organization_id)
        total_vehicles_res = await db.execute(total_vehicles_q)
        total_vehicles = total_vehicles_res.scalar_one_or_none() or 0
        
        active_journeys_q = select(func.count(Journey.id)).where(
            Journey.organization_id == current_user.organization_id,
            Journey.status == 'IN_PROGRESS'
        )
        active_journeys_res = await db.execute(active_journeys_q)
        active_journeys = active_journeys_res.scalar_one_or_none() or 0
        
        total_costs_q = select(func.sum(VehicleCost.amount)).where(
            VehicleCost.organization_id == current_user.organization_id,
            VehicleCost.date >= start_date.date() 
        )
        total_costs_res = await db.execute(total_costs_q)
        total_costs = total_costs_res.scalar_one_or_none() or 0.0
        
        maintenance_open_q = select(func.count(MaintenanceRequest.id)).where(
            MaintenanceRequest.organization_id == current_user.organization_id,
            MaintenanceRequest.status.in_(['PENDING', 'IN_PROGRESS'])
        )
        maintenance_open_res = await db.execute(maintenance_open_q)
        maintenance_open = maintenance_open_res.scalar_one_or_none() or 0

        return DashboardSummary(
            total_vehicles=total_vehicles,
            active_journeys=active_journeys,
            total_costs_last_30_days=total_costs,
            maintenance_open_requests=maintenance_open
        )
    except Exception as e:
        logging.error(f"Erro ao gerar dashboard summary: {e}", exc_info=True)
        return DashboardSummary(
            total_vehicles=0,
            active_journeys=0,
            total_costs_last_30_days=0.0,
            maintenance_open_requests=0
        )