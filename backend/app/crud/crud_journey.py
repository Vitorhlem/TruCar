from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List, Optional, Tuple
from datetime import date, timedelta

from app.models.journey_model import Journey
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.schemas.journey_schema import JourneyCreate, JourneyUpdate

async def create_journey(db: AsyncSession, *, journey_in: JourneyCreate, driver_id: int, organization_id: int) -> Optional[Journey]:
    vehicle_to_update = await db.get(Vehicle, journey_in.vehicle_id)

    if journey_in.start_engine_hours is not None:
        vehicle_to_update.custom_data = {"engine_hours": journey_in.start_engine_hours}
    
    vehicle_to_update.status = VehicleStatus.IN_USE
    db_journey = Journey(**journey_in.model_dump(), driver_id=driver_id, is_active=True, organization_id=organization_id, start_time=datetime.utcnow() 
)
    

    if not vehicle_to_update or vehicle_to_update.status != VehicleStatus.AVAILABLE or vehicle_to_update.organization_id != organization_id:
        return None
    
    vehicle_to_update.status = VehicleStatus.IN_USE
    db_journey = Journey(**journey_in.model_dump(), driver_id=driver_id, is_active=True, organization_id=organization_id)
    db.add(db_journey)
    db.add(vehicle_to_update)
    await db.commit()
    await db.refresh(db_journey)
    reloaded_journey = await get_journey(db, journey_id=db_journey.id, organization_id=organization_id)
    return reloaded_journey

# --- FUNÇÃO CORRIGIDA ---
async def end_journey(db: AsyncSession, *, journey_to_update: Journey, journey_in: JourneyUpdate) -> Optional[Tuple[Journey, Vehicle]]:
    vehicle_to_update = await db.get(Vehicle, journey_to_update.vehicle_id)
    if journey_in.end_engine_hours is not None:
        journey_to_update.end_engine_hours = journey_in.end_engine_hours
        vehicle_to_update.custom_data = {"engine_hours": journey_in.end_engine_hours}
    else:
        journey_to_update.end_mileage = journey_in.end_mileage
        vehicle_to_update.current_km = journey_in.end_mileage

    journey_to_update.end_time = func.now()
    journey_to_update.is_active = False
    vehicle_to_update.status = VehicleStatus.AVAILABLE

    if not vehicle_to_update:
        return None
    
    journey_to_update.end_mileage = journey_in.end_mileage
    journey_to_update.end_time = func.now()
    journey_to_update.is_active = False

    vehicle_to_update.status = VehicleStatus.AVAILABLE
    vehicle_to_update.current_km = journey_in.end_mileage
    
    db.add(journey_to_update)
    db.add(vehicle_to_update)
    
    await db.commit()
    await db.refresh(journey_to_update)
    await db.refresh(vehicle_to_update)
    
    return journey_to_update, vehicle_to_update

# ... (O resto do arquivo continua o mesmo)
async def get_journey(db: AsyncSession, *, journey_id: int, organization_id: int) -> Optional[Journey]:
    stmt = (
        select(Journey).where(Journey.id == journey_id, Journey.organization_id == organization_id)
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_journeys(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100, driver_id: int | None = None, vehicle_id: int | None = None, date_from: date | None = None, date_to: date | None = None) -> List[Journey]:
    stmt = select(Journey).where(Journey.organization_id == organization_id)
    if driver_id:
        stmt = stmt.where(Journey.driver_id == driver_id)
    if vehicle_id:
        stmt = stmt.where(Journey.vehicle_id == vehicle_id)
    if date_from:
        stmt = stmt.where(Journey.start_time >= date_from)
    if date_to:
        stmt = stmt.where(Journey.start_time < date_to + timedelta(days=1))
    stmt = (
        stmt.order_by(Journey.start_time.desc())
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_active_journeys(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[Journey]:
    stmt = (
        select(Journey).where(Journey.is_active == True, Journey.organization_id == organization_id)
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_active_journey_by_driver(db: AsyncSession, *, driver_id: int, organization_id: int) -> Optional[Journey]:
    stmt = (
        select(Journey).where(Journey.driver_id == driver_id, Journey.is_active == True, Journey.organization_id == organization_id)
        .options(selectinload(Journey.vehicle))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def delete_journey(db: AsyncSession, *, journey_id: int, organization_id: int) -> Journey | None:
    journey_to_delete = await get_journey(db, journey_id=journey_id, organization_id=organization_id)
    if journey_to_delete:
        await db.delete(journey_to_delete)
        await db.commit()
    return journey_to_delete