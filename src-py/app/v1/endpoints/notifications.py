from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, deps
from app.models.user_model import User
from app.schemas.notification_schema import NotificationPublic

router = APIRouter()

@router.get("/", response_model=List[NotificationPublic])
async def read_notifications(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retorna as notificações do utilizador logado, garantindo o isolamento da organização."""
    notifications = await crud.notification.get_notifications_for_user(
        db, user_id=current_user.id, organization_id=current_user.organization_id
    )
    return notifications

@router.get("/unread-count", response_model=int)
async def read_unread_notification_count(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retorna a contagem de notificações não lidas do utilizador logado."""
    count = await crud.notification.get_unread_notifications_count(
        db, user_id=current_user.id, organization_id=current_user.organization_id
    )
    return count

@router.post("/{notification_id}/read", response_model=NotificationPublic)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Marca uma notificação como lida, garantindo que ela pertence ao utilizador."""
    notification = await crud.notification.mark_notification_as_read(
        db, notification_id=notification_id, user_id=current_user.id, organization_id=current_user.organization_id
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada.")
    return notification

@router.post("/trigger-alerts", status_code=status.HTTP_202_ACCEPTED)
async def trigger_alerts_check_for_organization(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Dispara a verificação de alertas do sistema APENAS para a organização do gestor logado.
    (Idealmente, isto seria uma tarefa agendada, não um endpoint de API).
    """
    await crud.notification.run_system_checks_for_organization(
        db, organization_id=current_user.organization_id
    )
    return {"message": "Verificação de alertas para a sua organização foi iniciada."}