from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, text
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.models.notification_model import Notification
from app.models.user_model import User, UserRole
from app.models.vehicle_model import Vehicle
from app.models.journey_model import Journey
from app.models.organization_model import Organization

async def get_notifications_for_user(db: AsyncSession, *, user_id: int, organization_id: int) -> list[Notification]:
    """Busca todas as notificações de um utilizador dentro de uma organização."""
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id, Notification.organization_id == organization_id)
        .order_by(Notification.created_at.desc())
        .options(
            selectinload(Notification.user),
            selectinload(Notification.vehicle)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_unread_notifications_count(db: AsyncSession, *, user_id: int, organization_id: int) -> int:
    """Retorna a contagem de notificações não lidas de um utilizador dentro de uma organização."""
    stmt = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read == False,
        Notification.organization_id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalar_one()

async def mark_notification_as_read(db: AsyncSession, *, notification_id: int, user_id: int, organization_id: int) -> Notification | None:
    """Marca uma notificação como lida, garantindo que pertence ao utilizador e à organização correta."""
    notification = await db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.organization_id == organization_id
        )
    )
    if notification:
        notification.is_read = True
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
    return notification

async def create_alert_for_all_managers(db: AsyncSession, *, message: str, organization_id: int, vehicle_id: int | None = None):
    """Cria uma notificação para todos os gestores de uma organização específica."""
    if vehicle_id:
        existing_alert_stmt = select(Notification).where(
            Notification.related_vehicle_id == vehicle_id,
            Notification.message == message,
            Notification.is_read == False,
            Notification.organization_id == organization_id
        )
        if await db.scalar(existing_alert_stmt):
            return

    manager_stmt = select(User).where(
        User.role == UserRole.MANAGER,
        User.is_active == True,
        User.organization_id == organization_id
    )
    managers = (await db.execute(manager_stmt)).scalars().all()

    for manager in managers:
        new_notification = Notification(
            user_id=manager.id,
            message=message,
            related_vehicle_id=vehicle_id,
            organization_id=organization_id
        )
        db.add(new_notification)
    await db.commit()

async def run_system_checks_and_generate_alerts(db: AsyncSession):
    """
    Verifica as regras de negócio para TODAS as organizações e gera alertas.
    """
    print("Iniciando verificação de alertas do sistema para todas as organizações...")
    
    orgs = (await db.execute(select(Organization))).scalars().all()
    for org in orgs:
        print(f"A verificar alertas para a Organização: {org.name} (ID: {org.id})")
        
        # 1. Alerta: Veículos com manutenção por KM próxima
        km_threshold = 1000
        subquery = (
            select(Journey.vehicle_id, func.max(Journey.end_mileage).label("current_km"))
            .where(Journey.organization_id == org.id)
            .group_by(Journey.vehicle_id).subquery()
        )
        km_alert_stmt = (
            select(Vehicle, subquery.c.current_km)
            .join(subquery, Vehicle.id == subquery.c.vehicle_id)
            .where(
                Vehicle.organization_id == org.id,
                Vehicle.next_maintenance_km != None,
                subquery.c.current_km != None,
                (Vehicle.next_maintenance_km - subquery.c.current_km) <= km_threshold,
                (Vehicle.next_maintenance_km - subquery.c.current_km) > 0
            )
        )
        vehicles_for_km_alert = (await db.execute(km_alert_stmt)).all()
        for vehicle, current_km in vehicles_for_km_alert:
            km_remaining = vehicle.next_maintenance_km - current_km
            message = f"Manutenção por KM pendente para {vehicle.brand} {vehicle.model} (Placa: {vehicle.license_plate}). Faltam {km_remaining} KM."
            await create_alert_for_all_managers(db, message=message, organization_id=org.id, vehicle_id=vehicle.id)

        # 2. Alerta: Veículos com manutenção por Data próxima
        date_threshold = datetime.utcnow().date() + timedelta(days=14)
        vehicles_due_date_stmt = select(Vehicle).where(
            Vehicle.organization_id == org.id,
            Vehicle.next_maintenance_date != None,
            Vehicle.next_maintenance_date <= date_threshold
        )
        for vehicle in (await db.execute(vehicles_due_date_stmt)).scalars().all():
            message = f"Manutenção agendada para {vehicle.brand} {vehicle.model} (Placa: {vehicle.license_plate}) em {vehicle.next_maintenance_date.strftime('%d/%m/%Y')}."
            await create_alert_for_all_managers(db, message=message, organization_id=org.id, vehicle_id=vehicle.id)

    print("Verificação de alertas do sistema concluída.")