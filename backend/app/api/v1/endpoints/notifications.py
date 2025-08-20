from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.notification_schema import NotificationPublic

router = APIRouter()

@router.get("/unread-count", response_model=int)
async def get_unread_count(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> any:
    """Retorna a contagem de notificações não lidas do usuário logado."""
    count = await crud.notification.get_unread_notifications_count(db, user_id=current_user.id)
    return count

@router.get("/", response_model=List[NotificationPublic])
async def read_notifications(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    notifications = await crud.notification.get_notifications_for_user(db, user_id=current_user.id)
    return notifications

@router.post("/{notification_id}/read", response_model=NotificationPublic)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    notification = await crud.notification.mark_notification_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada.")
    return notification

@router.post("/trigger-alerts", status_code=status.HTTP_202_ACCEPTED)
async def trigger_alerts_check(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    await crud.notification.run_system_checks_and_generate_alerts(db)
    return {"message": "Verificação de alertas do sistema iniciada em segundo plano."}