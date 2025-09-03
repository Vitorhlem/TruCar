from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.organization_model import Organization
from app.models.user_model import User, UserRole
from app.schemas.organization_schema import OrganizationCreate, OrganizationUpdate


async def get(db: AsyncSession, *, id: int) -> Organization | None:
    """Busca uma organização pelo seu ID, carregando os utilizadores associados."""
    stmt = select(Organization).where(Organization.id == id).options(selectinload(Organization.users))
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_multi(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[Organization]:
    """
    Busca organizações, garantindo que a lista de utilizadores seja sempre a mais recente.
    """
    stmt = select(Organization).options(selectinload(Organization.users))

    if status:
        stmt = stmt.join(Organization.users).where(User.role == status).distinct()
    
    stmt = stmt.order_by(Organization.name).offset(skip).limit(limit)
    
    # --- CORREÇÃO DEFINITIVA ---
    # Adicionamos a opção 'populate_existing' para forçar o SQLAlchemy a 
    # atualizar os objetos em memória com os dados frescos da base de dados.
    result = await db.execute(stmt.execution_options(populate_existing=True))
    # --- FIM DA CORREÇÃO ---
    
    return result.scalars().unique().all()


async def get_organization_by_name(db: AsyncSession, name: str) -> Organization | None:
    """Busca uma organização pelo nome."""
    stmt = select(Organization).where(Organization.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, *, obj_in: OrganizationCreate) -> Organization:
    """Cria uma nova organização."""
    db_obj = Organization(**obj_in.model_dump(exclude_unset=True))
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update(
    db: AsyncSession, *, db_obj: Organization, obj_in: OrganizationUpdate
) -> Organization:
    """Atualiza uma organização."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj