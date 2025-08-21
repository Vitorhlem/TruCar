from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from app.models.vehicle_model import Vehicle
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate
from app.models.location_history_model import LocationHistory

# Em backend/app/crud/crud_vehicle.py
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.schemas.vehicle_schema import VehicleCreate

async def create_vehicle(
    db: AsyncSession, *, vehicle_in: VehicleCreate, organization_id: int
) -> Vehicle:
    """
    Cria um novo veículo, garantindo que a organization_id seja definida.
    """
    # Cria um dicionário a partir do schema Pydantic
    vehicle_data = vehicle_in.model_dump()
    
    # Adiciona a organization_id ao dicionário de dados
    db_vehicle = Vehicle(**vehicle_data, organization_id=organization_id)
    
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle

# ADICIONE ESTA FUNÇÃO COMPLETA
async def get_multi_by_org(
    db: AsyncSession,
    *,
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None
) -> tuple[list[Vehicle], int]:
    """
    Retorna uma lista paginada de veículos para uma organização e a contagem total.
    """
    # Query para buscar os veículos
    stmt = (
        select(Vehicle)
        .where(Vehicle.organization_id == organization_id)
    )
    
    # Query para contar o total de veículos (para a paginação)
    count_stmt = (
        select(func.count())
        .select_from(Vehicle)
        .where(Vehicle.organization_id == organization_id)
    )

    # Aplica o filtro de busca se ele existir
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.license_plate.ilike(search_term),
                Vehicle.identifier.ilike(search_term)
            )
        )
        count_stmt = count_stmt.where(
            or_(
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.license_plate.ilike(search_term),
                Vehicle.identifier.ilike(search_term)
            )
        )

    # Executa a contagem total
    total_count_result = await db.execute(count_stmt)
    total = total_count_result.scalar_one()

    # Aplica a paginação e executa a busca dos veículos
    stmt = stmt.offset(skip).limit(limit).order_by(Vehicle.id)
    vehicles_result = await db.execute(stmt)
    vehicles = vehicles_result.scalars().all()
    
    return vehicles, total

async def get_all_vehicles_by_org(
    db: AsyncSession, *, organization_id: int
) -> List[Vehicle]:
    """
    Retorna uma lista de todos os veículos para uma organização específica.
    """
    stmt = (
        select(Vehicle)
        .where(Vehicle.organization_id == organization_id)
        .order_by(Vehicle.id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_vehicle(
    db: AsyncSession, *, vehicle_id: int, organization_id: int
) -> Vehicle | None:
    """
    Busca um veículo específico pelo ID, garantindo que ele pertença à organização correta.
    """
    stmt = select(Vehicle).where(
        Vehicle.id == vehicle_id, 
        Vehicle.organization_id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_vehicle_by_license_plate(db: AsyncSession, *, license_plate: str, organization_id: int) -> Optional[Vehicle]:
    """Busca um veículo pela sua placa, garantindo que pertence à organização correta."""
    stmt = select(Vehicle).where(Vehicle.license_plate == license_plate, Vehicle.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_vehicles(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 10, search: str | None = None) -> List[Vehicle]:
    """Retorna uma lista de veículos de uma organização, com paginação e busca."""
    stmt = select(Vehicle).where(Vehicle.organization_id == organization_id)
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.license_plate.ilike(search_term)
            )
        )
    stmt = stmt.order_by(Vehicle.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_vehicles_count(db: AsyncSession, *, organization_id: int, search: str | None = None) -> int:
    """Retorna o número total de veículos de uma organização, aplicando o filtro de busca."""
    stmt = select(func.count()).select_from(Vehicle).where(Vehicle.organization_id == organization_id)
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.license_plate.ilike(search_term)
            )
        )
    result = await db.execute(stmt)
    return result.scalar_one()

async def update_vehicle(db: AsyncSession, *, db_vehicle: Vehicle, vehicle_in: VehicleUpdate) -> Vehicle:
    """Atualiza os dados de um veículo."""
    update_data = vehicle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle

async def delete_vehicle(db: AsyncSession, *, db_vehicle: Vehicle) -> Vehicle:
    """Deleta um veículo do banco de dados a partir do objeto."""
    await db.delete(db_vehicle)
    await db.commit()
    return db_vehicle

async def update_location(db: AsyncSession, *, vehicle_id: int, lat: float, lon: float):
    """Atualiza a última localização de um veículo e cria um registo de histórico."""
    # A verificação da organização deve ser feita no endpoint antes de chamar esta função
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        return

    vehicle.last_latitude = lat
    vehicle.last_longitude = lon
    db.add(vehicle)
    
    history_entry = LocationHistory(
        vehicle_id=vehicle_id,
        latitude=lat,
        longitude=lon,
        organization_id=vehicle.organization_id
    )
    db.add(history_entry)
    await db.commit()