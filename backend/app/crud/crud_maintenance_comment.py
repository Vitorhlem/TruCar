from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.maintenance_request_model import MaintenanceComment
from app.schemas.maintenance_schema import MaintenanceCommentCreate

async def create_comment(db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int) -> MaintenanceComment:
    """Cria um novo comentário, associando-o a um chamado, utilizador e organização."""
    db_obj = MaintenanceComment(
        **comment_in.model_dump(),
        request_id=request_id,
        user_id=user_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    # Recarrega com o utilizador para a resposta da API
    stmt = select(MaintenanceComment).where(MaintenanceComment.id == db_obj.id).options(selectinload(MaintenanceComment.user))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_comments_for_request(db: AsyncSession, *, request_id: int, organization_id: int) -> List[MaintenanceComment]:
    """Busca todos os comentários de um chamado específico dentro de uma organização."""
    stmt = (
        select(MaintenanceComment)
        .where(MaintenanceComment.request_id == request_id, MaintenanceComment.organization_id == organization_id)
        .order_by(MaintenanceComment.created_at.asc())
        .options(selectinload(MaintenanceComment.user))
    )
    result = await db.execute(stmt)
    return result.scalars().all()