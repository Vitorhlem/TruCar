from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User, UserRole
from app.models.organization_model import Organization
from app.models.journey_model import Journey
from app.models.vehicle_model import Vehicle
from app.models.maintenance_model import MaintenanceRequest
# Adicionamos o schema UserRegister que estava faltando
from app.schemas.user_schema import UserCreate, UserUpdate, UserRegister


# ===== FUNÇÃO DE REGISTRO QUE ESTAVA FALTANDO =====
async def create_new_organization_and_user(db: AsyncSession, *, user_in: UserRegister) -> User:
    """
    Cria uma nova organização e o primeiro usuário (gestor ou cliente) para ela
    em uma única transação atômica.
    """
    # Cria o objeto Organization
    db_org = Organization(name=user_in.organization_name, sector=user_in.sector)
    
    # Determina a role do usuário com base no setor
    user_role = UserRole.CLIENT if user_in.sector == 'frete' else UserRole.MANAGER

    # Cria o objeto User
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_role,
        # Associa diretamente o objeto da organização. SQLAlchemy gerencia a Foreign Key.
        organization=db_org 
    )
    
    db.add(db_org)
    db.add(db_user)
    
    # Um único commit salva ambos os objetos (Organização e Usuário) de forma segura.
    await db.commit()
    
    await db.refresh(db_user, ["organization"])
    return db_user
# ===== FIM DA FUNÇÃO ADICIONADA =====


async def get_user_by_email(db: AsyncSession, *, email: str, load_organization: bool = False) -> User | None:
    stmt = select(User).where(User.email == email)
    if load_organization:
        stmt = stmt.options(selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user(db: AsyncSession, *, user_id: int, organization_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id, User.organization_id == organization_id).options(selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_with_organization(db: AsyncSession, *, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id).options(selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[User]:
    stmt = (
        select(User)
        .where(User.organization_id == organization_id)
        .options(selectinload(User.organization))
        .order_by(User.id)
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_user(db: AsyncSession, *, user_in: UserCreate, organization_id: int, role: UserRole) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=role,
        organization_id=organization_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user, ["organization"])
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
    stmt = select(User).where(
        User.role == role,
        User.is_active == True,
        User.organization_id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_user(db: AsyncSession, *, db_user: User) -> User:
    await db.delete(db_user)
    await db.commit()
    return db_user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email=email, load_organization=True)
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