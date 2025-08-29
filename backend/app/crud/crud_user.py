from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.organization_model import Organization # Importe o modelo Organization

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
    """Calcula as estatísticas de um utilizador, adaptando-as ao setor da organização."""
    
    # 1. Busca o usuário e sua organização para saber o setor
    user = await get_user(db, user_id=user_id, organization_id=organization_id)
    if not user or not user.organization:
        return None

    # 2. Busca todas as jornadas finalizadas do usuário
    journeys_stmt = select(Journey).where(
        Journey.driver_id == user_id,
        Journey.organization_id == organization_id,
        Journey.is_active == False
    )
    journeys_result = await db.execute(journeys_stmt)
    journeys = journeys_result.scalars().all()

    total_journeys = len(journeys)
    
    # --- INÍCIO DA LÓGICA CONDICIONAL ---
    
    if user.organization.sector == 'agronegocio':
        # --- LÓGICA PARA AGRONEGÓCIO ---
        
        # Métrica Principal: Horas Totais
        total_value = sum(
            (j.end_engine_hours - j.start_engine_hours)
            for j in journeys if j.end_engine_hours is not None and j.start_engine_hours is not None
        )
        
        # Performance por Veículo (em Horas)
        performance_stmt = (
            select(
                Vehicle.brand, Vehicle.model, Vehicle.identifier,
                func.sum(Journey.end_engine_hours - Journey.start_engine_hours).label("total_value")
            )
            .join(Journey, Journey.vehicle_id == Vehicle.id)
            .where(Journey.driver_id == user_id, Journey.is_active == False)
            .group_by(Vehicle.id)
            .order_by(func.sum(Journey.end_engine_hours - Journey.start_engine_hours).desc())
        )
        performance_result = (await db.execute(performance_stmt)).all()
        
        performance_by_vehicle = [{
            "vehicle_info": f"{row.brand} {row.model} ({row.identifier})",
            "value": row.total_value or 0.0
        } for row in performance_result]

        stats_payload = {
            "total_journeys": total_journeys,
            "primary_metric_label": "Horas Totais Trabalhadas",
            "primary_metric_value": total_value,
            "primary_metric_unit": "Horas",
            "performance_by_vehicle": performance_by_vehicle,
        }

    else:
        # --- LÓGICA PARA SERVIÇOS E OUTROS (BASEADA EM KM) ---

        # Métrica Principal: KM Totais
        total_value = sum(
            (j.end_mileage - j.start_mileage)
            for j in journeys if j.end_mileage is not None and j.start_mileage is not None
        )

        # Performance por Veículo (em KM)
        performance_stmt = (
            select(
                Vehicle.brand, Vehicle.model, Vehicle.license_plate,
                func.sum(Journey.end_mileage - Journey.start_mileage).label("total_value")
            )
            .join(Journey, Journey.vehicle_id == Vehicle.id)
            .where(Journey.driver_id == user_id, Journey.is_active == False)
            .group_by(Vehicle.id)
            .order_by(func.sum(Journey.end_mileage - Journey.start_mileage).desc())
        )
        performance_result = (await db.execute(performance_stmt)).all()
        
        performance_by_vehicle = [{
            "vehicle_info": f"{row.brand} {row.model} ({row.license_plate})",
            "value": row.total_value or 0.0
        } for row in performance_result]
        
        # KPIs de Combustível (só fazem sentido para KM)
        # (Seu código original de cálculo de combustível pode ser inserido aqui)
        
        stats_payload = {
            "total_journeys": total_journeys,
            "primary_metric_label": "Distância Total Percorrida",
            "primary_metric_value": total_value,
            "primary_metric_unit": "km",
            "performance_by_vehicle": performance_by_vehicle,
            # Adicione aqui os KPIs de combustível se desejar
            "avg_km_per_liter": 0.0, # Substituir pelo cálculo real
            "avg_cost_per_km": 0.0, # Substituir pelo cálculo real
            "fleet_avg_km_per_liter": 0.0, # Substituir pelo cálculo real
        }
        
    # 3. Cálculos Comuns a Todos os Setores
    maintenance_count_stmt = select(func.count(MaintenanceRequest.id)).where(
        MaintenanceRequest.reported_by_id == user_id
    )
    maintenance_requests_count = (await db.execute(maintenance_count_stmt)).scalar_one_or_none() or 0

    stats_payload["maintenance_requests_count"] = maintenance_requests_count

    return stats_payload

async def get_leaderboard_data(db: AsyncSession, *, organization_id: int) -> dict:
    """
    Busca e calcula os dados do placar de líderes para uma organização,
    adaptando a métrica de performance ao setor.
    """
    org = await db.get(Organization, organization_id)
    if not org:
        return {"leaderboard": [], "primary_metric_unit": "N/A"}

    if org.sector == 'agronegocio':
        metric_calculation = func.sum(Journey.end_engine_hours - Journey.start_engine_hours)
        primary_metric_unit = "Horas"
    else:
        metric_calculation = func.sum(Journey.end_mileage - Journey.start_mileage)
        primary_metric_unit = "km"

    leaderboard_stmt = (
        select(
            User.id,
            User.full_name,
            User.avatar_url,
            func.count(Journey.id).label("total_journeys"),
            metric_calculation.label("primary_metric_value")
        )
        .join(Journey, User.id == Journey.driver_id)
        .where(
            User.organization_id == organization_id,
            User.role == UserRole.DRIVER,
            Journey.is_active == False
            # A condição de agregação foi REMOVIDA daqui
        )
        .group_by(User.id)
        # --- INÍCIO DA CORREÇÃO ---
        # A condição foi MOVIDA para a cláusula HAVING, que é executada após o GROUP BY
        .having(metric_calculation.is_not(None))
        # --- FIM DA CORREÇÃO ---
        .order_by(metric_calculation.desc().nullslast())
        .limit(50)
    )

    result = await db.execute(leaderboard_stmt)
    leaderboard_users = result.all()

    return {
        "leaderboard": leaderboard_users,
        "primary_metric_unit": primary_metric_unit
    }