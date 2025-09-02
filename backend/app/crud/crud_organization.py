from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# A importação do PlanStatus foi REMOVIDA
from app.models.organization_model import Organization
from app.schemas.organization_schema import OrganizationCreate


async def get_organization_by_name(db: AsyncSession, name: str) -> Organization | None:
    """Busca uma organização pelo nome."""
    stmt = select(Organization).where(Organization.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_organization(db: AsyncSession, *, id: int) -> Organization | None:
    """Busca uma organização pelo seu ID."""
    return await db.get(Organization, id)

async def get_organizations(
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> List[Organization]:
    """Busca organizações com paginação."""
    stmt = select(Organization).offset(skip).limit(limit).order_by(Organization.name)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_organization(db: AsyncSession, *, obj_in: OrganizationCreate) -> Organization:
    """Cria uma nova organização."""
    # Agora a criação é simples, sem se preocupar com plan_status
    db_org = Organization(name=obj_in.name, sector=obj_in.sector)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org