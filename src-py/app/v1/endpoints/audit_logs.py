from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import deps
from app.crud import crud_audit_log
from app.schemas.audit_log_schema import AuditLogPublic
from app.models.user_model import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[AuditLogPublic])
async def read_audit_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 50,
    resource_type: str = None,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Lista o histórico de auditoria da organização.
    Apenas gestores e admins podem ver.
    """
    logs = await crud_audit_log.get_multi_by_org(
        db=db, 
        organization_id=current_user.organization_id, 
        skip=skip, 
        limit=limit,
        resource_type=resource_type
    )
    
    # Enriquece o objeto com o nome do usuário para facilitar no frontend
    results = []
    for log in logs:
        log_public = AuditLogPublic.model_validate(log)
        if log.user:
            log_public.user_name = log.user.full_name
        else:
            log_public.user_name = "Sistema / Desconhecido"
        results.append(log_public)
        
    return results