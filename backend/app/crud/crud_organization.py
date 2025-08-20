from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.organization_model import Organization
from app.schemas.organization_schema import OrganizationCreate


async def create_organization(db: AsyncSession, *, obj_in: OrganizationCreate) -> Organization:
    """Cria uma nova organização."""
    # CORREÇÃO: Usamos 'obj_in' para aceder ao nome e ao setor
    db_org = Organization(name=obj_in.name, sector=obj_in.sector)
    
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org

async def get_organization_by_name(db: AsyncSession, name: str) -> Organization | None:
    stmt = select(Organization).where(Organization.name == name)
    return await db.scalar(stmt)