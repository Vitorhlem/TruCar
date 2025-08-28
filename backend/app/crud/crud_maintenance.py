from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.maintenance_model import MaintenanceRequest, MaintenanceComment
from app.models.vehicle_model import Vehicle
from app.models.user_model import User
from app.schemas.maintenance_schema import MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceCommentCreate

# --- CRUD para Solicitações de Manutenção ---

async def create_request(
    db: AsyncSession, *, request_in: MaintenanceRequestCreate, reporter_id: int, organization_id: int
) -> MaintenanceRequest:
    """Cria uma nova solicitação de manutenção e retorna o objeto completo."""
    vehicle = await db.get(Vehicle, request_in.vehicle_id)
    if not vehicle or vehicle.organization_id != organization_id:
        raise ValueError("Veículo não encontrado nesta organização.")

    db_obj = MaintenanceRequest(**request_in.model_dump(), reported_by_id=reporter_id, organization_id=organization_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj, ["reporter", "vehicle", "comments", "approver"])
    return db_obj

async def get_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> MaintenanceRequest | None:
    """Busca uma solicitação de manutenção específica, carregando todas as relações."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.id == request_id, MaintenanceRequest.organization_id == organization_id
    ).options(
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle),
        selectinload(MaintenanceRequest.comments).selectinload(MaintenanceComment.user)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_requests(
    db: AsyncSession, *, organization_id: int, search: str | None = None, skip: int = 0, limit: int = 100
) -> List[MaintenanceRequest]:
    """Busca todas as solicitações, carregando TODAS as relações necessárias."""
    stmt = select(MaintenanceRequest).where(MaintenanceRequest.organization_id == organization_id)
    if search:
        search_term = f"%{search}%"
        stmt = stmt.join(MaintenanceRequest.vehicle).where(
            or_(
                MaintenanceRequest.problem_description.ilike(search_term),
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term)
            )
        )
    stmt = stmt.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit).options(
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle),
        selectinload(MaintenanceRequest.comments).selectinload(MaintenanceComment.user)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_request_status(
    db: AsyncSession, *, db_obj: MaintenanceRequest, update_data: MaintenanceRequestUpdate, manager_id: int
) -> MaintenanceRequest:
    """Atualiza o status de uma solicitação e retorna o objeto completo."""
    db_obj.status = update_data.status
    db_obj.manager_notes = update_data.manager_notes
    db_obj.approver_id = manager_id
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj, ["reporter", "vehicle", "comments", "approver"])
    return db_obj

# --- CRUD PARA COMENTÁRIOS DE MANUTENÇÃO (ADICIONADO AQUI) ---

async def create_comment(
    db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int
) -> MaintenanceComment:
    """Cria um novo comentário, garantindo que a solicitação pertence à organização."""
    # A verificação de segurança agora funciona, pois 'get_request' está no mesmo ficheiro
    request_obj = await get_request(db, request_id=request_id, organization_id=organization_id)
    if not request_obj:
        raise ValueError("Solicitação de manutenção não encontrada.")

    db_obj = MaintenanceComment(
        **comment_in.model_dump(),
        request_id=request_id,
        user_id=user_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj, ["user"])
    return db_obj

async def get_comments_for_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> List[MaintenanceComment]:
    """Busca os comentários de uma solicitação, garantindo que a solicitação pertence à organização."""
    request_obj = await get_request(db, request_id=request_id, organization_id=organization_id)
    if not request_obj:
        return []
    
    stmt = select(MaintenanceComment).where(MaintenanceComment.request_id == request_id).order_by(MaintenanceComment.created_at.asc()).options(selectinload(MaintenanceComment.user))
    result = await db.execute(stmt)
    return result.scalars().all()