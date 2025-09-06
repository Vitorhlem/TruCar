from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from geopy.distance import geodesic # <-- NOVO IMPORT para calcular distância

from app.models.fuel_log_model import FuelLog, VerificationStatus
from app.models.vehicle_model import Vehicle
from app.models.user_model import User
from app.schemas.fuel_log_schema import FuelLogCreate, FuelLogUpdate, FuelProviderTransaction


# --- Funções CRUD para Abastecimento Manual (Seu código original, sem alterações) ---

async def create_fuel_log(db: AsyncSession, *, log_in: FuelLogCreate, user_id: int, organization_id: int) -> FuelLog:
    """Cria um novo registo de abastecimento manual."""
    db_obj = FuelLog(**log_in.model_dump(), user_id=user_id, organization_id=organization_id)
    db.add(db_obj)
    await db.commit()
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


# --- NOVAS FUNÇÕES PARA INTEGRAÇÃO COM CARTÃO DE COMBUSTÍVEL ---

async def _verify_transaction_location(
    vehicle_coords: Optional[tuple[float, float]],
    station_coords: tuple[float, float],
    threshold_km: float = 1.0
) -> VerificationStatus:
    """
    Compara a localização do veículo com a do posto.
    Retorna SUSPICIOUS se a distância for maior que o limite.
    """
    if not vehicle_coords or not vehicle_coords[0] or not vehicle_coords[1]:
        return VerificationStatus.UNVERIFIED # Não é possível verificar sem a localização do veículo
    
    distance = geodesic(vehicle_coords, station_coords).kilometers
    
    if distance > threshold_km:
        return VerificationStatus.SUSPICIOUS
    
    return VerificationStatus.VERIFIED


async def process_provider_transactions(db: AsyncSession, *, transactions: List[FuelProviderTransaction], organization_id: int):
    """
    Processa uma lista de transações de um provedor de combustível,
    cria os FuelLogs e realiza a verificação anti-fraude.
    """
    new_logs_count = 0
    for tx in transactions:
        # 1. Evita duplicados
        existing_log_stmt = select(FuelLog).where(FuelLog.provider_transaction_id == tx.transaction_id)
        existing_log = (await db.execute(existing_log_stmt)).scalars().first()
        if existing_log:
            continue

        # 2. Encontra o veículo pela placa
        vehicle_stmt = select(Vehicle).where(Vehicle.license_plate == tx.vehicle_license_plate, Vehicle.organization_id == organization_id)
        vehicle = (await db.execute(vehicle_stmt)).scalars().first()
        if not vehicle:
            continue # Pula transação se o veículo não for encontrado

        # 3. Encontra o motorista pelo CPF (ou outro identificador único)
        # NOTA: Assumimos que o seu model User terá um campo 'cpf'. Se usar outro, ajuste aqui.
        driver_stmt = select(User).where(User.cpf == tx.driver_cpf, User.organization_id == organization_id)
        driver = (await db.execute(driver_stmt)).scalars().first()
        if not driver:
            continue # Pula se o motorista não for encontrado
        
        # 4. Realiza a verificação de localização (anti-fraude)
        vehicle_location = (vehicle.last_latitude, vehicle.last_longitude)
        station_location = (tx.gas_station_latitude, tx.gas_station_longitude)
        verification_status = await _verify_transaction_location(vehicle_location, station_location)

        # 5. Cria o novo FuelLog com os dados da integração
        new_log = FuelLog(
            odometer=vehicle.current_km, # Usa o odômetro atual do veículo como aproximação
            liters=tx.liters,
            total_cost=tx.total_cost,
            vehicle_id=vehicle.id,
            user_id=driver.id,
            organization_id=organization_id,
            timestamp=tx.timestamp,
            # Campos específicos da integração
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
