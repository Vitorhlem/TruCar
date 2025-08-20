from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List

from app.models.maintenance_request_model import MaintenanceRequest
from app.models.vehicle_model import Vehicle
from app.schemas.maintenance_schema import MaintenanceRequestCreate, MaintenanceRequestUpdate

async def create_request(db: AsyncSession, *, request_in: MaintenanceRequestCreate, reporter_id: int, organization_id: int) -> MaintenanceRequest:
    """Cria uma nova solicitação de manutenção, associando-a a uma organização."""
    db_obj = MaintenanceRequest(
        **request_in.model_dump(),
        reported_by_id=reporter_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return await get_request(db=db, request_id=db_obj.id, organization_id=organization_id)

async def get_request(db: AsyncSession, *, request_id: int, organization_id: int) -> MaintenanceRequest | None:
    """Busca uma solicitação de manutenção específica de uma organização."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.id == request_id,
        MaintenanceRequest.organization_id == organization_id
    ).options(
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_requests(db: AsyncSession, *, organization_id: int, search: str | None = None) -> List[MaintenanceRequest]:
    """Busca todas as solicitações de uma organização, com filtro de busca."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.organization_id == organization_id
    ).order_by(MaintenanceRequest.created_at.desc())
    
    if search:
        search_term = f"%{search}%"
        stmt = stmt.join(MaintenanceRequest.vehicle).where(
            or_(
                MaintenanceRequest.problem_description.ilike(search_term),
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term)
            )
        )
    
    stmt = stmt.options(
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_requests_by_driver(db: AsyncSession, *, driver_id: int, organization_id: int, search: str | None = None) -> List[MaintenanceRequest]:
    """Busca as solicitações de um motorista específico dentro de uma organização."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.reported_by_id == driver_id,
        MaintenanceRequest.organization_id == organization_id
    ).order_by(MaintenanceRequest.created_at.desc())
    
    if search:
        search_term = f"%{search}%"
        stmt = stmt.join(MaintenanceRequest.vehicle).where(
            or_(
                MaintenanceRequest.problem_description.ilike(search_term),
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term)
            )
        )

    stmt = stmt.options(
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_request_status(db: AsyncSession, *, db_obj: MaintenanceRequest, update_data: MaintenanceRequestUpdate, manager_id: int) -> MaintenanceRequest:
    """Atualiza o status e as notas de uma solicitação."""
    db_obj.status = update_data.status
    db_obj.manager_notes = update_data.manager_notes
    db_obj.approver_id = manager_id
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_request(db: AsyncSession, *, request_id: int, organization_id: int) -> MaintenanceRequest | None:
    """Deleta uma solicitação de manutenção de uma organização."""
    request_to_delete = await get_request(db, request_id=request_id, organization_id=organization_id)
    if request_to_delete:
        await db.delete(request_to_delete)
        await db.commit()
    return request_to_delete