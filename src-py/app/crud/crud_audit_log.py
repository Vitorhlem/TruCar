from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List

from app.models.audit_log_model import AuditLog
from app.schemas.audit_log_schema import AuditLogCreate
from app.models.user_model import User

async def create(db: AsyncSession, *, log_in: AuditLogCreate) -> AuditLog:
    db_obj = AuditLog(**log_in.model_dump())
    db.add(db_obj)
    # Não fazemos commit aqui geralmente se for parte de outra transação, 
    # mas para logs é bom garantir que seja salvo mesmo se a operação principal falhar? 
    # Não, melhor seguir a transação principal.
    return db_obj

async def get_multi_by_org(
    db: AsyncSession, 
    *, 
    organization_id: int, 
    skip: int = 0, 
    limit: int = 100,
    resource_type: str = None
) -> List[AuditLog]:
    stmt = (
        select(AuditLog)
        .where(AuditLog.organization_id == organization_id)
        .options(selectinload(AuditLog.user)) # Carrega o usuário para mostrar o nome
        .order_by(desc(AuditLog.created_at))
    )
    
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
        
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()