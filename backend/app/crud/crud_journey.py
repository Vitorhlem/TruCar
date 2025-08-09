from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta # <-- A IMPORTAÇÃO QUE FALTAVA ESTÁ AQUI

from app.models.journey_model import Journey
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.schemas.journey_schema import JourneyCreate, JourneyUpdate

# --- Funções de Escrita (Create, Update) ---
async def create_journey(
    db: AsyncSession, *, journey_in: JourneyCreate, driver_id: int
) -> Optional[Journey]:
    # ... (código existente, sem alterações)
    vehicle_to_update = await db.get(Vehicle, journey_in.vehicle_id)
    if not vehicle_to_update or vehicle_to_update.status != VehicleStatus.AVAILABLE:
        return None 
    vehicle_to_update.status = VehicleStatus.IN_USE
    db_journey = Journey(**journey_in.model_dump(), driver_id=driver_id, is_active=True)
    db.add(db_journey)
    db.add(vehicle_to_update)
    await db.commit()
    await db.refresh(db_journey)
    reloaded_journey = await get_journey(db, journey_id=db_journey.id)
    return reloaded_journey

async def end_journey(
    db: AsyncSession, *, journey_to_update: Journey, journey_in: JourneyUpdate
) -> Optional[Journey]:
    # ... (código existente, sem alterações)
    vehicle_to_update = await db.get(Vehicle, journey_to_update.vehicle_id)
    if not vehicle_to_update:
        return None
    journey_to_update.end_mileage = journey_in.end_mileage
    journey_to_update.end_time = func.now()
    journey_to_update.is_active = False
    vehicle_to_update.status = VehicleStatus.AVAILABLE
    db.add(journey_to_update)
    db.add(vehicle_to_update)
    await db.commit()
    await db.refresh(journey_to_update)
    reloaded_journey = await get_journey(db, journey_id=journey_to_update.id)
    return reloaded_journey

# --- Funções de Leitura (Read) ---
async def get_journey(db: AsyncSession, journey_id: int) -> Optional[Journey]:
    # ... (código existente, sem alterações)
    stmt = (
        select(Journey).where(Journey.id == journey_id)
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_journeys(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    driver_id: int | None = None,
    vehicle_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None
) -> List[Journey]:
    """
    Retorna uma lista de todas as viagens, com filtros e paginação.
    """
    stmt = select(Journey)

    if driver_id:
        stmt = stmt.where(Journey.driver_id == driver_id)
    if vehicle_id:
        stmt = stmt.where(Journey.vehicle_id == vehicle_id)
    if date_from:
        stmt = stmt.where(Journey.start_time >= date_from)
    if date_to:
        # Adiciona um dia para incluir todo o dia final na busca
        stmt = stmt.where(Journey.start_time < date_to + timedelta(days=1))

    stmt = (
        stmt.order_by(Journey.start_time.desc())
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_active_journeys(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Journey]:
    # ... (código existente, sem alterações)
    stmt = (
        select(Journey).where(Journey.is_active == True)
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_active_journey_by_driver(db: AsyncSession, driver_id: int) -> Optional[Journey]:
    # ... (código existente, sem alterações)
    stmt = select(Journey).where(Journey.driver_id == driver_id, Journey.is_active == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def delete_journey(db: AsyncSession, *, journey_id: int) -> Journey | None:
    # ... (código existente, sem alterações)
    journey_to_delete = await get_journey(db, journey_id=journey_id)
    if journey_to_delete:
        await db.delete(journey_to_delete)
        await db.commit()
    return journey_to_delete