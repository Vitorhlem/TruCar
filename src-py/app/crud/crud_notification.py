# Em backend/app/crud/crud_notification.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List

from app.models.notification_model import Notification, NotificationType
from app.models.user_model import User, UserRole
from app.models.vehicle_model import Vehicle
from app.models.document_model import Document

# --- FUNÇÃO DE CRIAÇÃO ATUALIZADA ---
async def create_notification(
    db: AsyncSession,
    *,
    message: str,
    notification_type: NotificationType,
    organization_id: int,
    user_id: int | None = None,
    send_to_managers: bool = False,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
    related_vehicle_id: int | None = None
):
    """
    Cria uma notificação para um usuário específico OU para todos os gestores.
    Esta função agora gerencia seu próprio commit e é ideal para background tasks.
    """
    target_user_ids = []
    if user_id:
        target_user_ids.append(user_id)
        
    if send_to_managers:
        manager_stmt = select(User.id).where(
            User.organization_id == organization_id,
            User.role.in_([UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]),
            User.is_active == True
        )
        manager_ids = (await db.execute(manager_stmt)).scalars().all()
        target_user_ids.extend(manager_ids)

    unique_user_ids = set(target_user_ids)

    for uid in unique_user_ids:
        new_notification = Notification(
            organization_id=organization_id,
            user_id=uid,
            message=message,
            notification_type=notification_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            related_vehicle_id=related_vehicle_id
        )
        db.add(new_notification)
        
    await db.commit()
# --- FIM DA ATUALIZAÇÃO ---


# ... (o restante do arquivo, como run_system_checks_for_organization e outras funções, permanece o mesmo)
async def get_notifications_for_user(db: AsyncSession, *, user_id: int, organization_id: int) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id, Notification.organization_id == organization_id)
        .order_by(Notification.created_at.desc())
        .options(selectinload(Notification.vehicle))
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_unread_notifications_count(db: AsyncSession, *, user_id: int, organization_id: int) -> int:
    stmt = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read == False,
        Notification.organization_id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalar_one()

async def mark_notification_as_read(db: AsyncSession, *, notification_id: int, user_id: int, organization_id: int) -> Notification | None:
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id,
        Notification.organization_id == organization_id
    )
    notification = await db.scalar(stmt)
    
    if notification:
        notification.is_read = True
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
    return notification

async def run_system_checks_for_organization(db: AsyncSession, *, organization_id: int):
    print(f"A verificar alertas para a Organização ID: {organization_id}")
    
    date_threshold = datetime.utcnow().date() + timedelta(days=14)
    vehicles_due_date_stmt = select(Vehicle).where(
        Vehicle.organization_id == organization_id,
        Vehicle.next_maintenance_date != None,
        Vehicle.next_maintenance_date <= date_threshold
    )
    for vehicle in (await db.execute(vehicles_due_date_stmt)).scalars().all():
        message = f"Manutenção agendada para {vehicle.brand} {vehicle.model} em {vehicle.next_maintenance_date.strftime('%d/%m/%Y')}."
        await create_notification(db, message=message, notification_type=NotificationType.MAINTENANCE_DUE_DATE, organization_id=organization_id, send_to_managers=True, related_vehicle_id=vehicle.id)

    vehicles_due_km_stmt = select(Vehicle).where(
        Vehicle.organization_id == organization_id,
        Vehicle.next_maintenance_km != None,
        Vehicle.current_km != None,
        Vehicle.next_maintenance_km - Vehicle.current_km <= 500
    )
    for vehicle in (await db.execute(vehicles_due_km_stmt)).scalars().all():
        message = f"{vehicle.brand} {vehicle.model} está a {vehicle.next_maintenance_km - vehicle.current_km}km da próxima manutenção."
        await create_notification(db, message=message, notification_type=NotificationType.MAINTENANCE_DUE_KM, organization_id=organization_id, send_to_managers=True, related_vehicle_id=vehicle.id)

    doc_date_threshold = datetime.utcnow().date() + timedelta(days=30)
    docs_expiring_stmt = select(Document).where(
        Document.organization_id == organization_id,
        Document.expiry_date != None,
        Document.expiry_date <= doc_date_threshold
    ).options(selectinload(Document.vehicle), selectinload(Document.driver))
    
    for doc in (await db.execute(docs_expiring_stmt)).scalars().all():
        target_name = doc.vehicle.model if doc.vehicle else doc.driver.full_name
        message = f"O documento '{doc.document_type}' de {target_name} vence em {doc.expiry_date.strftime('%d/%m/%Y')}."
        await create_notification(db, message=message, notification_type=NotificationType.DOCUMENT_EXPIRING, organization_id=organization_id, send_to_managers=True, related_entity_type="document", related_entity_id=doc.id, related_vehicle_id=doc.vehicle_id)
        
    print(f"Verificação de alertas concluída para a Organização ID: {organization_id}")