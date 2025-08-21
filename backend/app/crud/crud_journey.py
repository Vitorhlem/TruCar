from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta

from app.models.journey_model import Journey
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.schemas.journey_schema import JourneyCreate, JourneyUpdate

# Exceções customizadas para uma arquitetura mais limpa
class VehicleNotAvailableError(Exception):
    pass

async def create_journey(
    db: AsyncSession, *, journey_in: JourneyCreate, driver_id: int, organization_id: int
) -> Journey:
    """Cria uma nova operação e atualiza o status do veículo para 'Em uso'."""
    if not journey_in.vehicle_id:
        raise ValueError("O ID do veículo é obrigatório.")
        
    vehicle = await db.get(Vehicle, journey_in.vehicle_id)
    if not vehicle or vehicle.organization_id != organization_id:
        raise ValueError("Veículo não encontrado ou não pertence à organização.")
        
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise VehicleNotAvailableError(f"O veículo {vehicle.brand} {vehicle.model} não está disponível.")

    db_journey = Journey(
        **journey_in.model_dump(exclude_unset=True),
        driver_id=driver_id,
        organization_id=organization_id,
        is_active=True,
        start_time=datetime.utcnow()
    )
    db.add(db_journey)
    
    vehicle.status = VehicleStatus.IN_USE
    db.add(vehicle)

    await db.commit()
    await db.refresh(db_journey, ['vehicle', 'driver'])
    return db_journey

async def end_journey(
    db: AsyncSession, *, db_journey: Journey, journey_in: JourneyUpdate
) -> Tuple[Journey, Vehicle]:
    """Finaliza uma operação, atualiza o status e o odómetro/horímetro do veículo."""
    update_data = journey_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_journey, field, value)
    
    db_journey.end_time = datetime.utcnow()
    db_journey.is_active = False
    db.add(db_journey)

    vehicle = db_journey.vehicle
    if vehicle:
        vehicle.status = VehicleStatus.AVAILABLE
        if journey_in.end_engine_hours is not None:
            vehicle.current_engine_hours = journey_in.end_engine_hours
        elif journey_in.end_mileage is not None:
            vehicle.current_km = journey_in.end_mileage
        
        db.add(vehicle)

    await db.commit()
    await db.refresh(db_journey, ['vehicle', 'driver'])
    
    return db_journey, vehicle

async def get_journey(db: AsyncSession, *, journey_id: int, organization_id: int) -> Optional[Journey]:
    """Busca uma viagem específica, garantindo que pertence à organização correta."""
    stmt = (
        select(Journey).where(Journey.id == journey_id, Journey.organization_id == organization_id)
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_journeys(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100, driver_id: int | None = None, vehicle_id: int | None = None, date_from: date | None = None, date_to: date | None = None) -> List[Journey]:
    """Busca todas as viagens de uma organização, com filtros."""
    stmt = select(Journey).where(Journey.organization_id == organization_id)
    if driver_id:
        stmt = stmt.where(Journey.driver_id == driver_id)
    if vehicle_id:
        stmt = stmt.where(Journey.vehicle_id == vehicle_id)
    if date_from:
        stmt = stmt.where(Journey.start_time >= date_from)
    if date_to:
        stmt = stmt.where(Journey.start_time < date_to + timedelta(days=1))
    
    final_stmt = (
        stmt.order_by(Journey.start_time.desc())
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle))
        .offset(skip).limit(limit)
    )
    result = await db.execute(final_stmt)
    return result.scalars().all()

async def get_active_journeys(db: AsyncSession, *, organization_id: int) -> list[Journey]:
    """Busca todas as operações ativas de uma organização."""
    stmt = (
        select(Journey)
        .where(Journey.organization_id == organization_id, Journey.is_active == True)
        .options(selectinload(Journey.vehicle), selectinload(Journey.driver))
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_active_journey_by_driver(db: AsyncSession, *, driver_id: int, organization_id: int) -> Journey | None:
    """Busca uma operação ativa para um motorista específico numa organização."""
    stmt = select(Journey).where(
        Journey.driver_id == driver_id,
        Journey.organization_id == organization_id,
        Journey.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def delete_journey(db: AsyncSession, *, journey_to_delete: Journey) -> Journey:
    """Exclui uma viagem e, se ela estiver ativa, atualiza o status do veículo."""
    vehicle = journey_to_delete.vehicle
    if journey_to_delete.is_active and vehicle:
        vehicle.status = VehicleStatus.AVAILABLE
        db.add(vehicle)

    await db.delete(journey_to_delete)
    await db.commit()
    return journey_to_delete