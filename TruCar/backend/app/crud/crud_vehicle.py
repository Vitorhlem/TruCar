from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.vehicle_model import Vehicle
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate

# --- Funções de Leitura (Read) ---

async def get_vehicle_by_license_plate(db: AsyncSession, license_plate: str) -> Optional[Vehicle]:
    """Busca um veículo pela sua placa."""
    result = await db.execute(select(Vehicle).filter(Vehicle.license_plate == license_plate))
    return result.scalar_one_or_none()

async def get_vehicle(db: AsyncSession, vehicle_id: int) -> Optional[Vehicle]:
    """Busca um veículo pelo seu ID."""
    result = await db.execute(select(Vehicle).filter(Vehicle.id == vehicle_id))
    return result.scalar_one_or_none()

async def get_all_vehicles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    """Retorna uma lista de todos os veículos cadastrados, com paginação."""
    result = await db.execute(select(Vehicle).offset(skip).limit(limit))
    return result.scalars().all()


# --- Funções de Escrita (Create, Update, Delete) ---

async def create_vehicle(db: AsyncSession, vehicle_in: VehicleCreate) -> Vehicle:
    """Cria um novo veículo no banco de dados."""
    db_vehicle = Vehicle(**vehicle_in.model_dump())
    # O status default 'AVAILABLE' é aplicado automaticamente pelo modelo
    
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    
    return db_vehicle

async def update_vehicle(
    db: AsyncSession, *, db_vehicle: Vehicle, vehicle_in: VehicleUpdate
) -> Vehicle:
    """Atualiza os dados de um veículo."""
    # Converte o schema de entrada para um dicionário
    update_data = vehicle_in.model_dump(exclude_unset=True)
    
    # Itera sobre os dados recebidos e atualiza o objeto do banco
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
        
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    
    return db_vehicle

async def delete_vehicle(db: AsyncSession, vehicle_id: int) -> Optional[Vehicle]:
    """Deleta um veículo do banco de dados."""
    vehicle_to_delete = await get_vehicle(db, vehicle_id=vehicle_id)
    if vehicle_to_delete:
        await db.delete(vehicle_to_delete)
        await db.commit()
    return vehicle_to_delete