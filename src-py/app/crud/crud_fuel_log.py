from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from geopy.distance import geodesic
from app import crud
from app.models.fuel_log_model import FuelLog, VerificationStatus
from app.models.vehicle_model import Vehicle
from app.models.user_model import User
from app.schemas.vehicle_cost_schema import VehicleCostCreate
from app.schemas.fuel_log_schema import FuelLogCreate, FuelLogUpdate, FuelProviderTransaction

async def check_abnormal_consumption(db: AsyncSession, *, fuel_log: FuelLog, vehicle: Vehicle) -> tuple[bool, str]:
    """
    Verifica se o consumo de um abastecimento é anormal em comparação com a média do veículo.
    Retorna (True, "mensagem de alerta") se for anormal.
    """
    previous_log_stmt = (
        select(FuelLog)
        .where(
            FuelLog.vehicle_id == vehicle.id,
            FuelLog.timestamp < fuel_log.timestamp
        )
        .order_by(FuelLog.timestamp.desc())
        .limit(1)
    )
    previous_log = (await db.execute(previous_log_stmt)).scalars().first()
    
    if not previous_log or not previous_log.odometer:
        return (False, "") # Não há dados suficientes para comparar

    km_travelled = fuel_log.odometer - previous_log.odometer
    if km_travelled <= 0 or fuel_log.liters <= 0:
        return (False, "")
        
    current_consumption = km_travelled / fuel_log.liters

    avg_consumption_stmt = select(func.avg((FuelLog.odometer - func.lag(FuelLog.odometer, 1, FuelLog.odometer).over(order_by=FuelLog.timestamp)) / FuelLog.liters)) \
        .where(FuelLog.vehicle_id == vehicle.id, FuelLog.id != fuel_log.id)
    
    historical_avg = (await db.execute(avg_consumption_stmt)).scalar_one_or_none()
    
    if not historical_avg or historical_avg <= 0:
        return (False, "")

    if current_consumption < (historical_avg * 0.75):
        message = f"Consumo anormal para {vehicle.brand} {vehicle.model}: {current_consumption:.2f} km/l (Média: {historical_avg:.2f} km/l)."
        return (True, message)
        
    return (False, "")

async def create_fuel_log(db: AsyncSession, *, log_in: FuelLogCreate, user_id: int, organization_id: int) -> FuelLog:
    """Cria um novo registo de abastecimento manual e um custo associado."""
    
    db_obj = FuelLog(
        **log_in.model_dump(exclude={"user_id"}), 
        user_id=user_id, 
        organization_id=organization_id
    )

    db.add(db_obj)
    await db.flush()  # Garante que o db_obj tenha um ID antes de usá-lo

    cost_obj_in = VehicleCostCreate( #
        description=f"Abastecimento em {db_obj.timestamp.strftime('%d/%m/%Y')}",
        amount=db_obj.total_cost,
        date=db_obj.timestamp.date(),
        cost_type="Combustível",
    )
    
    await crud.vehicle_cost.create_cost( #
        db, 
        obj_in=cost_obj_in, 
        vehicle_id=db_obj.vehicle_id, 
        organization_id=organization_id,
        commit=False  # Evita o commit duplo
    )

    await db.commit()
    await db.refresh(db_obj, ["user", "vehicle"])
    return db_obj

async def get_fuel_log(db: AsyncSession, *, log_id: int, organization_id: int) -> Optional[FuelLog]:
    stmt = select(FuelLog).where(FuelLog.id == log_id, FuelLog.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]:
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
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    
    
    
    await db.refresh(db_obj, ["user", "vehicle"])

    return db_obj

async def remove_fuel_log(db: AsyncSession, *, db_obj: FuelLog) -> FuelLog:
    await db.delete(db_obj)
    await db.commit()
    return db_obj



async def _verify_transaction_location(
    vehicle_coords: Optional[tuple[float, float]],
    station_coords: tuple[float, float],
    threshold_km: float = 1.0
) -> VerificationStatus:
    if not vehicle_coords or not vehicle_coords[0] or not vehicle_coords[1]:
        return VerificationStatus.UNVERIFIED
    
    distance = geodesic(vehicle_coords, station_coords).kilometers
    
    if distance > threshold_km:
        return VerificationStatus.SUSPICIOUS
    
    return VerificationStatus.VERIFIED


async def process_provider_transactions(db: AsyncSession, *, transactions: List[FuelProviderTransaction], organization_id: int):
    new_logs_count = 0
    for tx in transactions:
        existing_log_stmt = select(FuelLog).where(FuelLog.provider_transaction_id == tx.transaction_id)
        existing_log = (await db.execute(existing_log_stmt)).scalars().first()
        if existing_log:
            continue

        vehicle_stmt = select(Vehicle).where(Vehicle.license_plate == tx.vehicle_license_plate, Vehicle.organization_id == organization_id)
        vehicle = (await db.execute(vehicle_stmt)).scalars().first()
        if not vehicle:
            continue

        driver_stmt = select(User).where(User.employee_id == tx.driver_employee_id, User.organization_id == organization_id)
        driver = (await db.execute(driver_stmt)).scalars().first()
        if not driver:
            continue
        
        vehicle_location = (vehicle.last_latitude, vehicle.last_longitude)
        station_location = (tx.gas_station_latitude, tx.gas_station_longitude)
        verification_status = await _verify_transaction_location(vehicle_location, station_location)

        new_log = FuelLog(
            odometer=vehicle.current_km,
            liters=tx.liters,
            total_cost=tx.total_cost,
            vehicle_id=vehicle.id,
            user_id=driver.id,
            organization_id=organization_id,
            timestamp=tx.timestamp,
            provider_name="Ticket Log (Simulado)",
            provider_transaction_id=tx.transaction_id,
            gas_station_name=tx.gas_station_name,
            gas_station_latitude=tx.gas_station_latitude,
            gas_station_longitude=tx.gas_station_longitude,
            verification_status=verification_status,
            source= "INTEGRATION"
        )
        db.add(new_log)
        new_logs_count += 1

    await db.commit()
    return {"new_logs_processed": new_logs_count}