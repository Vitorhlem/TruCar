from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.maintenance_request_model import MaintenanceComment
from app.schemas.maintenance_schema import MaintenanceCommentCreate

async def create_comment(
    db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int
) -> MaintenanceComment:
    """Cria um novo comentário, garantindo que a solicitação pertence à organização."""
    # Validação de segurança: verifica se a solicitação existe na organização do usuário
    request_obj = await get_request(db, request_id=request_id, organization_id=organization_id)
    if not request_obj:
        raise ValueError("Solicitação de manutenção não encontrada.")

    db_obj = MaintenanceComment(
        **comment_in.model_dump(),
        request_id=request_id,
        user_id=user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj, ["user"])
    return db_obj



async def get_comments_for_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> List[MaintenanceComment]:
    """Busca os comentários de uma solicitação, garantindo que a solicitação pertence à organização."""
    # Validação de segurança: primeiro busca a solicitação para garantir o acesso
    request_obj = await get_request(db, request_id=request_id, organization_id=organization_id)
    if not request_obj:
        return [] # Retorna lista vazia se o usuário não tiver acesso à solicitação
    
    stmt = select(MaintenanceComment).where(MaintenanceComment.request_id == request_id).order_by(MaintenanceComment.created_at.asc()).options(selectinload(MaintenanceComment.user))
    result = await db.execute(stmt)
    return result.scalars().all()