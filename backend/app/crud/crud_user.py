from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User, UserRole
from app.models.journey_model import Journey
from app.models.vehicle_model import Vehicle
from app.models.fuel_log_model import FuelLog
from app.models.maintenance_model import MaintenanceRequest
from app.schemas.user_schema import UserCreate, UserUpdate


async def get_user_by_email(
    db: AsyncSession, *, email: str, load_organization: bool = False
) -> User | None:
    """
    Busca um utilizador pelo seu email.
    Se load_organization for True, carrega o relacionamento com a organização.
    """
    stmt = select(User).where(User.email == email)
    
    # Lógica de otimização que estava em falta
    if load_organization:
        stmt = stmt.options(selectinload(User.organization))
        
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user(db: AsyncSession, *, user_id: int, organization_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id, User.organization_id == organization_id).options(selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_with_organization(db: AsyncSession, *, user_id: int) -> User | None:
    """Busca um utilizador e a sua organização associada."""
    stmt = select(User).where(User.id == user_id).options(selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_users(
    db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
) -> List[User]:
    """Retorna uma lista de utilizadores, carregando a organização de cada um."""
    stmt = (
        select(User)
        .where(User.organization_id == organization_id)
        .options(selectinload(User.organization)) # <-- Eager loading
        .order_by(User.id)
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_user(
    db: AsyncSession, *, user_in: UserCreate, organization_id: int, role: UserRole
) -> User:
    """Cria um novo utilizador associado a uma organização."""
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=role, # A role é passada como argumento, não vem do user_in
        organization_id=organization_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user, ["organization"]) # Garante o carregamento da relação
    return db_user



async def update_user(db: AsyncSession, *, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user, ["organization"])
    return db_user

async def get_users_by_role(db: AsyncSession, *, organization_id: int, role: UserRole) -> List[User]:
    """Busca todos os utilizadores com uma função específica dentro de uma organização."""
    stmt = select(User).where(
        User.role == role,
        User.is_active == True,
        User.organization_id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_user(
    db: AsyncSession, *, db_user: User, user_in: UserUpdate
) -> User:
    """Atualiza os dados de um utilizador."""
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, *, db_user: User) -> User:
    """Deleta um utilizador."""
    await db.delete(db_user)
    await db.commit()
    return db_user

async def authenticate(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    
    is_correct_password = await run_in_threadpool(verify_password, password, user.hashed_password)
    if not is_correct_password:
        return None
        
    return user

async def get_user_stats(db: AsyncSession, *, user_id: int, organization_id: int) -> dict | None:
    """Calcula as estatísticas de um utilizador, garantindo que pertence à organização."""
    user = await get_user(db, user_id=user_id, organization_id=organization_id)
    if not user:
        return None 

    # Total de Viagens e KM
    total_stats_stmt = select(
        func.count(Journey.id), func.sum(Journey.end_mileage - Journey.start_mileage)
    ).where(Journey.driver_id == user_id, Journey.organization_id == organization_id, Journey.is_active == False)
    result = (await db.execute(total_stats_stmt)).first()
    total_journeys = result[0] if result else 0
    total_km = result[1] if result and result[1] is not None else 0.0

    # Cálculos de Abastecimento
    fuel_stats_stmt = select(
        func.sum(FuelLog.liters), func.sum(FuelLog.total_cost)
    ).where(FuelLog.user_id == user_id, FuelLog.organization_id == organization_id)
    total_liters, total_cost = (await db.execute(fuel_stats_stmt)).first() or (0, 0)
    total_liters = total_liters or 0.0
    total_cost = total_cost or 0.0
    
    # Chamados de Manutenção
    maintenance_count_stmt = select(func.count(MaintenanceRequest.id)).where(
        MaintenanceRequest.reported_by_id == user_id, MaintenanceRequest.organization_id == organization_id
    )
    maintenance_requests_count = (await db.execute(maintenance_count_stmt)).scalar_one()

    # Médias da Frota (da organização)
    fleet_km_stmt = select(func.sum(Journey.end_mileage - Journey.start_mileage)).where(Journey.is_active == False, Journey.organization_id == organization_id)
    fleet_liters_stmt = select(func.sum(FuelLog.liters)).where(FuelLog.organization_id == organization_id)
    total_fleet_km = (await db.execute(fleet_km_stmt)).scalar_one() or 0.0
    total_fleet_liters = (await db.execute(fleet_liters_stmt)).scalar_one() or 0.0

    # KPIs Finais
    avg_km_per_liter = (total_km / total_liters) if total_liters > 0 else 0.0
    avg_cost_per_km = (total_cost / total_km) if total_km > 0 else 0.0
    fleet_avg_km_per_liter = (total_fleet_km / total_fleet_liters) if total_fleet_liters > 0 else 0.0

    # KM por veículo
    km_by_vehicle_stmt = (
        select(
            Vehicle.brand, Vehicle.model, Vehicle.license_plate,
            func.sum(Journey.end_mileage - Journey.start_mileage).label("total_km")
        )
        .join(Journey, Journey.vehicle_id == Vehicle.id)
        .where(Journey.driver_id == user_id, Journey.organization_id == organization_id, Journey.is_active == False)
        .group_by(Vehicle.id)
        .order_by(func.sum(Journey.end_mileage - Journey.start_mileage).desc())
    )
    km_by_vehicle_result = (await db.execute(km_by_vehicle_stmt)).all()
    
    journeys_by_vehicle = [{
        "vehicle_info": f"{row.brand} {row.model} ({row.license_plate})",
        "km_driven_in_vehicle": row.total_km
    } for row in km_by_vehicle_result]

    return {
        "total_journeys": total_journeys,
        "total_km_driven": total_km,
        "journeys_by_vehicle": journeys_by_vehicle,
        "maintenance_requests_count": maintenance_requests_count,
        "avg_km_per_liter": avg_km_per_liter,
        "avg_cost_per_km": avg_cost_per_km,
        "fleet_avg_km_per_liter": fleet_avg_km_per_liter
    }

    six_months_ago = datetime.utcnow() - timedelta(days=180)
    fuel_cost_stmt = (
        select(
            func.to_char(FuelLog.timestamp, 'YYYY-MM').label('month'),
            func.sum(FuelLog.total_cost).label('total_cost')
        )
        .where(FuelLog.timestamp >= six_months_ago)
    )
    # Se o usuário for um motorista, filtra apenas os seus próprios registros
    if current_user.role == UserRole.DRIVER:
        fuel_cost_stmt = fuel_cost_stmt.where(FuelLog.user_id == current_user.id)
        
    fuel_cost_stmt = fuel_cost_stmt.group_by('month').order_by('month')
    fuel_cost_result = await db.execute(fuel_cost_stmt)
    fuel_cost_last_6_months = [{"month": row.month, "total_cost": row.total_cost} for row in fuel_cost_result]

    return {
        "kpis": kpis,
        "fuel_cost_last_6_months": fuel_cost_last_6_months,
        # ... (outros dados)
    }