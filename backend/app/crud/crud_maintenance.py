from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List

from app.models.maintenance_model import MaintenanceRequest, MaintenanceComment
from app.models.vehicle_model import Vehicle
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
        # A CORREÇÃO CRUCIAL: Carregamos todas as relações que o schema Public precisa
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle),
        selectinload(MaintenanceRequest.comments).selectinload(MaintenanceComment.user)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_requests_by_driver(
    db: AsyncSession, *, driver_id: int, organization_id: int, search: str | None = None
) -> List[MaintenanceRequest]:
    """Busca as solicitações de um motorista específico dentro de uma organização."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.reported_by_id == driver_id,
        MaintenanceRequest.organization_id == organization_id
    )
    
    if search:
        # Lógica de busca pode ser adicionada aqui também, se necessário
        pass

    stmt = stmt.order_by(MaintenanceRequest.created_at.desc()).options(
        selectinload(MaintenanceRequest.vehicle)
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


# --- CRUD para Comentários de Manutenção ---


