from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta

from app.models.journey_model import Journey
from app.models.vehicle_model import Vehicle, VehicleStatus
# A LINHA QUE FALTAVA PARA O EAGER LOADING:
from app.models.user_model import User
from app.schemas.journey_schema import JourneyCreate, JourneyUpdate
from app.models.implement_model import Implement, ImplementStatus



# Exceções customizadas para uma arquitetura mais limpa
class VehicleNotAvailableError(Exception):
    pass

async def create_journey(
    db: AsyncSession, *, journey_in: JourneyCreate, driver_id: int, organization_id: int
) -> Journey:
    
    """Cria uma nova operação e atualiza o status do veículo para 'Em uso'."""
    if journey_in.implement_id:
        implement = await db.get(Implement, journey_in.implement_id)
        if not implement or implement.organization_id != organization_id:
            raise ValueError("Implemento não encontrado.")
        
        if implement.status != ImplementStatus.AVAILABLE:
            raise VehicleNotAvailableError(f"O implemento {implement.name} não está disponível.")
        
        # Altera o status do implemento
        implement.status = ImplementStatus.IN_USE
        db.add(implement)
    
    if not journey_in.vehicle_id:
        raise ValueError("O ID do veículo é obrigatório.")
        
    vehicle = await db.get(Vehicle, journey_in.vehicle_id)
    if not vehicle or vehicle.organization_id != organization_id:
        raise ValueError("Maquinário não encontrado.")
        
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise VehicleNotAvailableError(f"O maquinário {vehicle.brand} {vehicle.model} não está disponível.")

    journey_data = journey_in.model_dump(exclude_unset=True)
    
    # Lógica explícita para garantir que o valor inicial correto seja usado
    if journey_in.start_engine_hours is not None:
        journey_data['start_mileage'] = vehicle.current_km # Usa o KM atual como base
    else:
        journey_data['start_mileage'] = journey_in.start_mileage or vehicle.current_km

    db_journey = Journey(
        **journey_data,
        driver_id=driver_id,
        organization_id=organization_id,
        is_active=True,
        start_time=datetime.utcnow()
    )
    db.add(db_journey)
    
    vehicle.status = VehicleStatus.IN_USE
    db.add(vehicle)

    await db.commit()
    await db.refresh(db_journey, ['vehicle', 'driver', 'implement'])
    return db_journey
async def end_journey(
    db: AsyncSession, *, db_journey: Journey, journey_in: JourneyUpdate
) -> Tuple[Journey, Vehicle]:
    """Finaliza uma operação, atualiza o status E o odómetro/horímetro do veículo."""
    
    print(f"--- INICIANDO FINALIZAÇÃO DA JORNADA {db_journey.id} ---")
    print(f"Payload recebido: {journey_in.model_dump()}")

    # --- INÍCIO DA CORREÇÃO DEFINITIVA ---

    # 1. ATUALIZAR A JORNADA
    # Define os valores finais para a operação que está terminando.
    db_journey.end_time = datetime.utcnow()
    db_journey.is_active = False
    if journey_in.end_engine_hours is not None:
        db_journey.end_engine_hours = journey_in.end_engine_hours
    if journey_in.end_mileage is not None:
        db_journey.end_mileage = journey_in.end_mileage
    
    db.add(db_journey)
    print(f"Jornada ID {db_journey.id} marcada como finalizada com end_engine_hours = {db_journey.end_engine_hours}")

    # 2. ATUALIZAR O VEÍCULO (MAQUINÁRIO)
    # O horímetro final da operação se torna o NOVO horímetro ATUAL do maquinário.
    updated_vehicle = None
    if db_journey.vehicle_id:
        vehicle = await db.get(Vehicle, db_journey.vehicle_id)
        if vehicle:
            print(f"Veículo ID {vehicle.id} encontrado. Horímetro ANTES: {vehicle.current_engine_hours}")
            vehicle.status = VehicleStatus.AVAILABLE
            
            # A lógica principal:
            if journey_in.end_engine_hours is not None:
                vehicle.current_engine_hours = journey_in.end_engine_hours
                print(f"!!! ATUALIZANDO HORÍMETRO DO VEÍCULO PARA: {vehicle.current_engine_hours} !!!")
            
            elif journey_in.end_mileage is not None:
                vehicle.current_km = journey_in.end_mileage
                print(f"!!! ATUALIZANDO KM DO VEÍCULO PARA: {vehicle.current_km} !!!")

            db.add(vehicle)
            updated_vehicle = vehicle

    # 3. ATUALIZAR O IMPLEMENTO
    if db_journey.implement_id:
        implement = await db.get(Implement, db_journey.implement_id)
        if implement:
            implement.status = ImplementStatus.AVAILABLE
            db.add(implement)

    # --- FIM DA CORREÇÃO DEFINITIVA ---

    await db.commit()
    print("--- COMMIT REALIZADO COM SUCESSO ---")
    
    await db.refresh(db_journey, ['vehicle', 'driver', 'implement'])
    
    return db_journey, updated_vehicle


async def get_journey(db: AsyncSession, *, journey_id: int, organization_id: int) -> Optional[Journey]:
    """Busca uma viagem específica, garantindo que pertence à organização correta."""
    stmt = (
        select(Journey).where(Journey.id == journey_id, Journey.organization_id == organization_id)
        .options(selectinload(Journey.driver), selectinload(Journey.vehicle), selectinload(Journey.implement))
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
        .options(selectinload(Journey.driver).selectinload(User.organization), selectinload(Journey.vehicle), selectinload(Journey.implement)) # <-- Eager loading
        .offset(skip).limit(limit)
    )
    result = await db.execute(final_stmt)
    return result.scalars().all()

async def get_active_journeys(db: AsyncSession, *, organization_id: int) -> list[Journey]:
    """Busca todas as operações ativas de uma organização."""
    stmt = (
        select(Journey)
        .where(Journey.organization_id == organization_id, Journey.is_active == True)
        .options(selectinload(Journey.vehicle), selectinload(Journey.driver), selectinload(Journey.implement))
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