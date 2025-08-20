from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.fuel_log_model import FuelLog
from app.schemas.fuel_log_schema import FuelLogCreate

async def create_fuel_log(db: AsyncSession, *, log_in: FuelLogCreate, user_id: int, organization_id: int) -> FuelLog:
    # Adicionamos 'organization_id' ao criar um novo registo
    db_obj = FuelLog(**log_in.model_dump(), user_id=user_id, organization_id=organization_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    stmt = select(FuelLog).where(FuelLog.id == db_obj.id).options(
        selectinload(FuelLog.user), selectinload(FuelLog.vehicle)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_fuel_logs(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]:
    """Busca todos os registos de abastecimento de uma organização (para gestores)."""
    stmt = (
        select(FuelLog)
        # Adicionamos o filtro por organização
        .where(FuelLog.organization_id == organization_id)
        .order_by(FuelLog.timestamp.desc())
        .options(selectinload(FuelLog.user), selectinload(FuelLog.vehicle))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_fuel_logs_by_user(db: AsyncSession, *, user_id: int, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]:
    """Busca os registos de abastecimento de um utilizador específico dentro de uma organização."""
    stmt = (
        select(FuelLog)
        # Garantimos que a busca é por utilizador E pela organização correta
        .where(FuelLog.user_id == user_id, FuelLog.organization_id == organization_id)
        .order_by(FuelLog.timestamp.desc())
        .options(selectinload(FuelLog.user), selectinload(FuelLog.vehicle))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()