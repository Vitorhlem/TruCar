from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy import update as sql_update # <--- CORREÇÃO 1: Alias para evitar conflito com a função update abaixo
from typing import List

from app.models.vehicle_model import Vehicle
from app.models.part_model import InventoryItem # <--- CORREÇÃO 2: Import correto do Modelo (está em part_model)
from app.schemas.telemetry_schema import TelemetryPayload
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate


async def get(db: AsyncSession, *, vehicle_id: int, organization_id: int) -> Vehicle | None:
    """Busca um veículo pelo ID, garantindo que pertence à organização."""
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(
    db: AsyncSession,
    *,
    organization_id: int,
    skip: int = 0,
    limit: int = 8,
    search: str | None = None
) -> List[Vehicle]:
    stmt = select(Vehicle).where(Vehicle.organization_id == organization_id)

    if search and search.strip():
        search_term = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Vehicle.brand).like(search_term),
                func.lower(Vehicle.model).like(search_term),
                func.lower(Vehicle.license_plate).like(search_term),
                func.lower(Vehicle.identifier).like(search_term)
            )
        )

    stmt = stmt.order_by(Vehicle.brand).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def count_by_org(db: AsyncSession, *, organization_id: int, search: str | None = None) -> int:
    """Conta o número total de veículos para paginação, considerando a busca."""
    stmt = select(func.count()).select_from(Vehicle).where(Vehicle.organization_id == organization_id)

    if search and search.strip():
        search_term = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Vehicle.brand).like(search_term),
                func.lower(Vehicle.model).like(search_term),
                func.lower(Vehicle.license_plate).like(search_term),
                func.lower(Vehicle.identifier).like(search_term)
            )
        )
    
    result = await db.execute(stmt)
    return result.scalar_one()

async def count(db: AsyncSession, *, organization_id: int) -> int:
    """Implementa o método 'count' genérico."""
    return await count_by_org(db, organization_id=organization_id)

async def update_vehicle_from_telemetry(db: AsyncSession, *, payload: TelemetryPayload) -> Vehicle | None:
    """Encontra um veículo pelo seu telemetry_device_id e atualiza seus dados."""
    stmt = select(Vehicle).where(Vehicle.telemetry_device_id == payload.device_id)
    result = await db.execute(stmt)
    vehicle_obj = result.scalar_one_or_none()

    if not vehicle_obj:
        print(f"AVISO: Recebida telemetria de um dispositivo não registrado: {payload.device_id}")
        return None

    vehicle_obj.last_latitude = payload.latitude
    vehicle_obj.last_longitude = payload.longitude
    if payload.engine_hours > (vehicle_obj.current_engine_hours or 0):
        vehicle_obj.current_engine_hours = payload.engine_hours
    
    db.add(vehicle_obj)
    await db.commit()
    await db.refresh(vehicle_obj)
    return vehicle_obj

async def create_with_owner(db: AsyncSession, *, obj_in: VehicleCreate, organization_id: int) -> Vehicle:
    """Cria um novo veículo associado a uma organização."""
    db_obj = Vehicle(**obj_in.model_dump())
    db_obj.organization_id = organization_id

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
    
async def update(db: AsyncSession, *, db_vehicle: Vehicle, vehicle_in: VehicleUpdate) -> Vehicle:
    """Atualiza os dados de um veículo."""
    update_data = vehicle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle

async def remove(db: AsyncSession, *, db_vehicle: Vehicle) -> Vehicle:
    """Deleta um veículo, desvinculando itens do inventário antes."""
    
    # 1. Desvincular itens instalados (Setar installed_on_vehicle_id = NULL)
    # CORREÇÃO: Usamos 'sql_update' para chamar o SQLAlchemy, não a nossa função local
    stmt = sql_update(InventoryItem).where(InventoryItem.installed_on_vehicle_id == db_vehicle.id).values(installed_on_vehicle_id=None)
    await db.execute(stmt)
    
    # 2. Agora é seguro deletar o veículo
    await db.delete(db_vehicle)
    await db.commit()
    return db_vehicle