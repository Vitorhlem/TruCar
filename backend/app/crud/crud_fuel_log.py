from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.fuel_log_model import FuelLog
from app.schemas.fuel_log_schema import FuelLogCreate, FuelLogUpdate

async def create_fuel_log(db: AsyncSession, *, log_in: FuelLogCreate, user_id: int, organization_id: int) -> FuelLog:
    """Cria um novo registo de abastecimento."""
    db_obj = FuelLog(**log_in.model_dump(), user_id=user_id, organization_id=organization_id)
    db.add(db_obj)
    await db.commit()
    # Otimização: Usamos refresh com as relações em vez de fazer uma nova query
    await db.refresh(db_obj, ["user", "vehicle"])
    return db_obj

async def get_fuel_log(db: AsyncSession, *, log_id: int, organization_id: int) -> Optional[FuelLog]:
    """Busca um único registo de abastecimento pelo ID, dentro de uma organização."""
    stmt = select(FuelLog).where(FuelLog.id == log_id, FuelLog.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]:
    """Busca todos os registos de abastecimento de uma organização (para gestores)."""
    stmt = (
        select(FuelLog)
        .where(FuelLog.organization_id == organization_id)
        .order_by(FuelLog.timestamp.desc())
        .options(selectinload(FuelLog.user), selectinload(FuelLog.vehicle))
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_multi_by_user(db: AsyncSession, *, user_id: int, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]:
    """Busca os registos de abastecimento de um utilizador específico dentro de uma organização."""
    stmt = (
        select(FuelLog)
        .where(FuelLog.user_id == user_id, FuelLog.organization_id == organization_id)
        .order_by(FuelLog.timestamp.desc())
        .options(selectinload(FuelLog.user), selectinload(FuelLog.vehicle))
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_fuel_log(db: AsyncSession, *, db_obj: FuelLog, obj_in: FuelLogUpdate) -> FuelLog:
    """Atualiza um registo de abastecimento."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_fuel_log(db: AsyncSession, *, db_obj: FuelLog) -> FuelLog:
    """Remove um registo de abastecimento."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj