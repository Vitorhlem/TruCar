from datetime import datetime, timedelta, timezone # Adicionado timezone
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, TYPE_CHECKING, Optional

from app.core.security import get_password_hash, verify_password, create_password_reset_token, PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
from app.models.user_model import User, UserRole
from app.models.organization_model import Organization

if TYPE_CHECKING:
    from app.schemas.user_schema import UserCreate, UserUpdate, UserRegister
    from app.models.journey_model import Journey
    from app.models.maintenance_model import MaintenanceRequest
    from app.models.vehicle_model import Vehicle
    from app.models.alert_model import Alert
    from app.models.achievement_model import Achievement, UserAchievement
    from app.schemas.dashboard_schema import DriverMetrics, DriverRankEntry, AchievementStatus


async def get(db: AsyncSession, *, id: int, organization_id: int | None = None) -> User | None:
    stmt = select(User).where(User.id == id)
    if organization_id:
        stmt = stmt.where(User.organization_id == organization_id)
    stmt = stmt.options(selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, *, email: str, load_organization: bool = False) -> User | None:
    stmt = select(User).where(User.email == email)
    if load_organization:
        stmt = stmt.options(selectinload(User.organization))
    result = await db.execute(stmt)

    return result.scalars().first()

async def set_password_reset_token(db: AsyncSession, *, user: User) -> User:
    """Gera e define um token de redefinição de senha para um usuário."""
    token = create_password_reset_token(email=user.email)
    
    # CORREÇÃO: Usando a constante importada para definir o tempo de expiração
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    
    user.reset_password_token = token
    user.reset_password_token_expires_at = expire_at
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

async def get_multi_by_org(db: AsyncSession, *, organization_id: int | None = None, skip: int = 0, limit: int = 100) -> List[User]:
    stmt = (
        select(User)
        .options(selectinload(User.organization))
        .order_by(User.full_name)
    )
    if organization_id:
        stmt = stmt.where(User.organization_id == organization_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_users_by_role(
    db: AsyncSession,
    *,
    role: UserRole,
    organization_id: int | None = None,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    stmt = select(User).where(
        User.role == role,
        User.is_active == True,
        User.organization_id.is_not(None) # <-- CORREÇÃO APLICADA AQUI
    ).options(selectinload(User.organization))

    if organization_id:
        stmt = stmt.where(User.organization_id == organization_id)
    
    stmt = stmt.order_by(User.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create(db: AsyncSession, *, user_in: "UserCreate", organization_id: int, role: UserRole) -> User:
    from app.schemas.user_schema import UserCreate
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

async def create_new_organization_and_user(db: AsyncSession, *, user_in: "UserRegister") -> User:
    """Cria uma nova organização e o primeiro utilizador (CLIENTE_DEMO) para ela."""
    from app.schemas.user_schema import UserRegister
    db_org = Organization(name=user_in.organization_name, sector=user_in.sector)
    user_role = UserRole.CLIENTE_DEMO

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_role,
        organization=db_org 
    )
    
    db.add(db_org)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user, ["organization"])
    return db_user


async def update(db: AsyncSession, *, db_user: User, user_in: "UserUpdate") -> User:
    from app.schemas.user_schema import UserUpdate
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
    
async def update_password(db: AsyncSession, *, db_user: User, new_password: str) -> User:
    """Atualiza a senha de um utilizador."""
    hashed_password = get_password_hash(new_password)
    db_user.hashed_password = hashed_password
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email=email, load_organization=True)
    if not user:
        return None
    is_correct_password = await run_in_threadpool(verify_password, password, user.hashed_password)
    if not is_correct_password:
        return None
    return user

async def get_leaderboard_data(db: AsyncSession, *, organization_id: int) -> dict:
    from app.models.journey_model import Journey
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
            User.id, User.full_name, User.avatar_url,
            func.count(Journey.id).label("total_journeys"),
            metric_calculation.label("primary_metric_value")
        )
        .join(Journey, User.id == Journey.driver_id)
        .where(
            User.organization_id == organization_id,
            User.role == UserRole.DRIVER,
            Journey.is_active == False
        )
        .group_by(User.id)
        .having(metric_calculation.is_not(None))
        .order_by(metric_calculation.desc().nullslast())
        .limit(50)
    )
    result = await db.execute(leaderboard_stmt)
    leaderboard_users = result.all()
    return { "leaderboard": leaderboard_users, "primary_metric_unit": primary_metric_unit }

async def get_driver_metrics(db: AsyncSession, *, user: User) -> "DriverMetrics":
    from app.models.journey_model import Journey
    from app.models.alert_model import Alert
    from app.schemas.dashboard_schema import DriverMetrics

    today = datetime.utcnow()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    org = user.organization
    
    if org.sector == 'agronegocio':
        metric_col = func.sum(Journey.end_engine_hours - Journey.start_engine_hours)
    else:
        metric_col = func.sum(Journey.end_mileage - Journey.start_mileage)

    metric_stmt = select(metric_col).where(
        Journey.driver_id == user.id,
        Journey.start_time >= start_of_month
    )
    primary_metric = (await db.execute(metric_stmt)).scalar_one_or_none() or 0
    
    alerts_stmt = select(func.count(Alert.id)).where(
        Alert.driver_id == user.id,
        Alert.timestamp >= start_of_month
    )
    alert_count = (await db.execute(alerts_stmt)).scalar_one_or_none() or 0

    fuel_efficiency = 8.5 

    return DriverMetrics(
        distance=primary_metric if org.sector != 'agronegocio' else 0,
        hours=primary_metric if org.sector == 'agronegocio' else 0,
        fuel_efficiency=fuel_efficiency,
        alerts=alert_count
    )

async def get_driver_ranking_context(db: AsyncSession, *, user: User) -> List["DriverRankEntry"]:
    from app.schemas.dashboard_schema import DriverRankEntry
    leaderboard_data = await get_leaderboard_data(db, organization_id=user.organization_id)
    full_leaderboard = leaderboard_data.get("leaderboard", [])

    try:
        current_user_index = next(i for i, driver in enumerate(full_leaderboard) if driver.id == user.id)
    except StopIteration:
        return [] 

    start_index = max(0, current_user_index - 2)
    end_index = min(len(full_leaderboard), current_user_index + 3)

    context_list = []
    for i in range(start_index, end_index):
        driver_data = full_leaderboard[i]
        context_list.append(DriverRankEntry(
            rank=i + 1,
            name=driver_data.full_name,
            metric=driver_data.primary_metric_value,
            is_current_user=(driver_data.id == user.id)
        ))
    return context_list

async def get_driver_achievements(db: AsyncSession, *, user: User) -> List["AchievementStatus"]:
    from app.models.achievement_model import Achievement, UserAchievement
    from app.schemas.dashboard_schema import AchievementStatus

    all_achievements_stmt = select(Achievement)
    all_achievements = (await db.execute(all_achievements_stmt)).scalars().all()

    unlocked_achievements_stmt = select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    unlocked_ids = set((await db.execute(unlocked_achievements_stmt)).scalars().all())

    status_list = []
    for ach in all_achievements:
        status_list.append(AchievementStatus(
            title=ach.title,
            icon=ach.icon,
            unlocked=(ach.id in unlocked_ids)
        ))
    return status_list

async def remove(db: AsyncSession, *, db_user: User) -> User:
    await db.delete(db_user)
    await db.commit()
    return db_user

async def activate_user(db: AsyncSession, *, user_to_activate: User) -> User:
    """Muda o papel de um utilizador de CLIENTE_DEMO para CLIENTE_ATIVO."""
    user_to_activate.role = UserRole.CLIENTE_ATIVO
    db.add(user_to_activate)
    await db.commit()
    await db.refresh(user_to_activate)
    return user_to_activate

async def count_by_org(db: AsyncSession, *, organization_id: int, role: UserRole | None = None) -> int:
    """Conta utilizadores numa organização, opcionalmente filtrando por papel."""
    stmt = select(func.count()).select_from(User).where(User.organization_id == organization_id)
    if role:
        stmt = stmt.where(User.role == role)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_user_stats(db: AsyncSession, *, user_id: int, organization_id: int) -> dict | None:
    """Calcula as estatísticas de um utilizador, adaptando-as ao setor da organização."""
    from app.models.journey_model import Journey
    from app.models.maintenance_model import MaintenanceRequest
    from app.models.vehicle_model import Vehicle

    user = await get(db, id=user_id, organization_id=organization_id)
    if not user or not user.organization:
        return None

    journeys_stmt = select(Journey).where(
        Journey.driver_id == user_id,
        Journey.organization_id == organization_id,
        Journey.is_active == False
    )
    journeys_result = await db.execute(journeys_stmt)
    journeys = journeys_result.scalars().all()
    total_journeys = len(journeys)
    
    stats_payload = {}
    if user.organization.sector == 'agronegocio':
        total_value = sum((j.end_engine_hours - j.start_engine_hours) for j in journeys if j.end_engine_hours is not None and j.start_engine_hours is not None)
        
        performance_stmt = (
            select(Vehicle.brand, Vehicle.model, Vehicle.identifier, func.sum(Journey.end_engine_hours - Journey.start_engine_hours).label("total_value"))
            .join(Journey, Journey.vehicle_id == Vehicle.id).where(Journey.driver_id == user_id, Journey.is_active == False).group_by(Vehicle.id)
            .order_by(func.sum(Journey.end_engine_hours - Journey.start_engine_hours).desc())
        )
        performance_result = (await db.execute(performance_stmt)).all()
        performance_by_vehicle = [{"vehicle_info": f"{row.brand} {row.model} ({row.identifier})", "value": row.total_value or 0.0} for row in performance_result]
        
        stats_payload.update({
            "primary_metric_label": "Horas Totais Trabalhadas", "primary_metric_value": total_value,
            "primary_metric_unit": "Horas", "performance_by_vehicle": performance_by_vehicle,
        })
    else: # Para 'servicos' e 'frete'
        total_value = sum((j.end_mileage - j.start_mileage) for j in journeys if j.end_mileage is not None and j.start_mileage is not None)
        
        performance_stmt = (
            select(Vehicle.brand, Vehicle.model, Vehicle.license_plate, func.sum(Journey.end_mileage - Journey.start_mileage).label("total_value"))
            .join(Journey, Journey.vehicle_id == Vehicle.id).where(Journey.driver_id == user_id, Journey.is_active == False).group_by(Vehicle.id)
            .order_by(func.sum(Journey.end_mileage - Journey.start_mileage).desc())
        )
        performance_result = (await db.execute(performance_stmt)).all()
        performance_by_vehicle = [{"vehicle_info": f"{row.brand} {row.model} ({row.license_plate})", "value": row.total_value or 0.0} for row in performance_result]

        stats_payload.update({
            "primary_metric_label": "Distância Total Percorrida", "primary_metric_value": total_value,
            "primary_metric_unit": "km", "performance_by_vehicle": performance_by_vehicle,
        })

    maintenance_count_stmt = select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.reported_by_id == user_id)
    maintenance_requests_count = (await db.execute(maintenance_count_stmt)).scalar_one_or_none() or 0
    
    stats_payload.update({
        "total_journeys": total_journeys,
        "maintenance_requests_count": maintenance_requests_count
    })
    return stats_payload

