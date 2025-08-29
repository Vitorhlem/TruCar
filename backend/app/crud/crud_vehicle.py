from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from typing import List

from app.models.vehicle_model import Vehicle
from app.schemas.telemetry_schema import TelemetryPayload
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate

class CRUDVehicle:
    
    async def get_multi_by_org(
        self,
        db: AsyncSession,
        *,
        organization_id: int,
        skip: int = 0,
        limit: int = 8,
        search: str | None = None
    ) -> List[Vehicle]:
        print(f"--- BUSCANDO VEÍCULOS PARA A ORGANIZATION_ID: {organization_id} ---")

        stmt = select(Vehicle).where(Vehicle.organization_id == organization_id)

        # --- INÍCIO DA CORREÇÃO ---
        # Aplica o filtro de busca APENAS se o termo de busca tiver conteúdo.
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
        # --- FIM DA CORREÇÃO ---

        stmt = stmt.order_by(Vehicle.brand).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_by_org(self, db: AsyncSession, *, organization_id: int, search: str | None = None) -> int:
        """
        Conta o número total de veículos para paginação, considerando a busca.
        """
        stmt = select(func.count()).select_from(Vehicle).where(Vehicle.organization_id == organization_id)

        # --- INÍCIO DA CORREÇÃO ---
        # Aplica o filtro de busca APENAS se o termo de busca tiver conteúdo.
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
        # --- FIM DA CORREÇÃO ---
        
        result = await db.execute(stmt)
        return result.scalar_one()

    async def update_vehicle_from_telemetry(self, db: AsyncSession, *, payload: TelemetryPayload) -> Vehicle | None:
        """
        Encontra um veículo pelo seu telemetry_device_id e atualiza seus dados.
        """
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

    async def create_with_owner(self, db: AsyncSession, *, obj_in: VehicleCreate, organization_id: int) -> Vehicle:
        """Cria um novo veículo associado a uma organização."""
        
        # --- INÍCIO DA CORREÇÃO ---
        # 1. Cria o objeto a partir do payload do frontend
        db_obj = Vehicle(**obj_in.model_dump())
        
        # 2. Atribui a organization_id de forma explícita e garantida
        db_obj.organization_id = organization_id
        # --- FIM DA CORREÇÃO ---

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        print(f"--- VEÍCULO CRIADO COM SUCESSO! ID: {db_obj.id}, ORG ID: {db_obj.organization_id} ---")
        
        return db_obj
        
    async def get(self, db: AsyncSession, *, vehicle_id: int, organization_id: int) -> Vehicle | None:
        """Busca um veículo pelo ID, garantindo que pertence à organização."""
        stmt = select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.organization_id == organization_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def update(self, db: AsyncSession, *, db_vehicle: Vehicle, vehicle_in: VehicleUpdate) -> Vehicle:
        """Atualiza os dados de um veículo."""
        update_data = vehicle_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)
        db.add(db_vehicle)
        await db.commit()
        await db.refresh(db_vehicle)
        return db_vehicle

    async def remove(self, db: AsyncSession, *, db_vehicle: Vehicle) -> Vehicle:
        """Deleta um veículo do banco de dados."""
        await db.delete(db_vehicle)
        await db.commit()
        return db_vehicle

vehicle = CRUDVehicle()
