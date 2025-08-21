from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.organization_model import Organization
from app.schemas.organization_schema import OrganizationCreate

async def get_organization_by_name(db: AsyncSession, name: str) -> Organization | None:
    """Busca uma organização pelo nome (usado para garantir nomes únicos)."""
    stmt = select(Organization).where(Organization.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_organization(db: AsyncSession, *, id: int) -> Organization | None:
    """Busca uma organização pelo seu ID."""
    return await db.get(Organization, id)

async def create_organization(db: AsyncSession, *, obj_in: OrganizationCreate) -> Organization:
    """Cria uma nova organização."""
    db_org = Organization(name=obj_in.name, sector=obj_in.sector)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org