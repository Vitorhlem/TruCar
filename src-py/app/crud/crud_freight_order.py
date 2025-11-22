from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from app.models.freight_order_model import FreightOrder, FreightStatus
from app.models.journey_model import Journey, JourneyType
from app.models.stop_point_model import StopPoint, StopPointStatus
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.models.user_model import User
from app.schemas.freight_order_schema import FreightOrderCreate, FreightOrderUpdate


# --- HELPER PARA RECARREGAR O OBJETO COMPLETO ---
async def _reload_order_with_relations(db: AsyncSession, order_id: int) -> FreightOrder:
    stmt = (
        select(FreightOrder)
        .where(FreightOrder.id == order_id)
        .options(
            selectinload(FreightOrder.client),
            selectinload(FreightOrder.stop_points),
            selectinload(FreightOrder.vehicle),
            selectinload(FreightOrder.driver),
            selectinload(FreightOrder.journeys)
        )
        .execution_options(populate_existing=True)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_with_stops(db: AsyncSession, *, obj_in: FreightOrderCreate, organization_id: int) -> FreightOrder:
    freight_order_data = obj_in.model_dump(exclude={"stop_points"})
    db_freight_order = FreightOrder(**freight_order_data, organization_id=organization_id, status=FreightStatus.OPEN)
    db.add(db_freight_order)
    
    await db.flush() 

    for stop_point_data in obj_in.stop_points:
        db_stop_point = StopPoint(
            **stop_point_data.model_dump(), 
            freight_order_id=db_freight_order.id
        )
        db.add(db_stop_point)
        
    await db.commit()
    return await _reload_order_with_relations(db, db_freight_order.id)


async def get(db: AsyncSession, *, id: int, organization_id: int) -> FreightOrder | None:
    stmt = (
        select(FreightOrder)
        .where(FreightOrder.id == id, FreightOrder.organization_id == organization_id)
        .options(
            selectinload(FreightOrder.client),
            selectinload(FreightOrder.vehicle),
            selectinload(FreightOrder.driver),
            selectinload(FreightOrder.stop_points),
            selectinload(FreightOrder.journeys)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FreightOrder]:
    stmt = (
        select(FreightOrder)
        .where(FreightOrder.organization_id == organization_id)
        .options(
            selectinload(FreightOrder.client),
            selectinload(FreightOrder.vehicle),
            selectinload(FreightOrder.driver),
            selectinload(FreightOrder.stop_points),
        )
        .order_by(FreightOrder.id.desc())
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# --- FUNÇÃO CORRIGIDA PARA EVITAR ERROS EM /OPEN ---
async def get_multi_by_status(db: AsyncSession, *, organization_id: int, status: FreightStatus) -> List[FreightOrder]:
    stmt = (
        select(FreightOrder)
        .where(
            FreightOrder.organization_id == organization_id,
            FreightOrder.status == status
        )
        .options(
            selectinload(FreightOrder.client),
            selectinload(FreightOrder.stop_points),
            # Carregamento defensivo de vehicle e driver
            selectinload(FreightOrder.vehicle),
            selectinload(FreightOrder.driver)
        )
        .order_by(FreightOrder.scheduled_start_time.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_pending_by_driver(db: AsyncSession, *, driver_id: int, organization_id: int) -> List[FreightOrder]:
    stmt = (
        select(FreightOrder)
        .where(
            FreightOrder.driver_id == driver_id,
            FreightOrder.organization_id == organization_id,
            FreightOrder.status.in_([FreightStatus.CLAIMED, FreightStatus.IN_TRANSIT])
        )
        .options(
            selectinload(FreightOrder.client),
            selectinload(FreightOrder.vehicle),
            selectinload(FreightOrder.stop_points)
        )
        .order_by(FreightOrder.scheduled_start_time)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update(db: AsyncSession, *, db_obj: FreightOrder, obj_in: FreightOrderUpdate) -> FreightOrder:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    
    return await _reload_order_with_relations(db, db_obj.id)
    
async def claim_order(db: AsyncSession, *, order: FreightOrder, driver: User, vehicle: Vehicle) -> FreightOrder:
    if order.status != FreightStatus.OPEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este frete não está mais aberto para atribuição.")
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O veículo selecionado não está disponível.")

    order.driver_id = driver.id
    order.vehicle_id = vehicle.id
    order.status = FreightStatus.CLAIMED
    db.add(order)
    
    vehicle.status = VehicleStatus.IN_USE
    db.add(vehicle)
    
    await db.commit()
    
    return await _reload_order_with_relations(db, order.id)

async def start_journey_for_stop(db: AsyncSession, *, order: FreightOrder, stop: StopPoint, vehicle: Vehicle) -> Journey:
    if order.status == FreightStatus.CLAIMED:
        order.status = FreightStatus.IN_TRANSIT
        db.add(order)
        
    new_journey = Journey(
        vehicle_id=vehicle.id,
        driver_id=order.driver_id,
        organization_id=order.organization_id,
        freight_order_id=order.id,
        start_mileage=vehicle.current_km,
        start_engine_hours=vehicle.current_engine_hours,
        start_time=datetime.utcnow(),
        is_active=True,
        trip_type=JourneyType.FREE_ROAM
    )
    db.add(new_journey)
    await db.commit()
    
    await db.refresh(new_journey, attribute_names=["driver", "vehicle"])
    
    return new_journey

async def complete_stop_point(db: AsyncSession, *, order: FreightOrder, stop: StopPoint, journey: Journey, end_mileage: int) -> StopPoint:
    stop.status = StopPointStatus.COMPLETED
    stop.actual_arrival_time = datetime.utcnow()
    db.add(stop)
    
    journey.is_active = False
    journey.end_time = datetime.utcnow()
    if end_mileage is not None:
        journey.end_mileage = end_mileage
    db.add(journey)
    
    if order.vehicle and end_mileage is not None:
        order.vehicle.current_km = end_mileage
        db.add(order.vehicle)

    all_stops_completed = all(s.status == StopPointStatus.COMPLETED for s in order.stop_points)
    if all_stops_completed:
        order.status = FreightStatus.DELIVERED
        if order.vehicle:
            order.vehicle.status = VehicleStatus.AVAILABLE
            db.add(order.vehicle)
        db.add(order)
        
    await db.commit()
    await db.refresh(stop)
    return stop