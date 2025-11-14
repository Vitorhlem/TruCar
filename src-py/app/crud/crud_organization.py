from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

# Importar as novas ferramentas
from app.core.security_utils import encrypt_data, decrypt_data
from app.models.organization_model import Organization
from app.schemas.organization_schema import OrganizationCreate, OrganizationUpdate, OrganizationFuelIntegrationUpdate
from app.models.user_model import User, UserRole


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
    """Busca organizações, garantindo que a lista de utilizadores seja sempre a mais recente."""
    stmt = select(Organization).options(selectinload(Organization.users))

    if status:
        stmt = stmt.join(Organization.users).where(User.role == status).distinct()
    
    stmt = stmt.order_by(Organization.name).offset(skip).limit(limit)
    
    result = await db.execute(stmt.execution_options(populate_existing=True))
    
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


# --- NOVAS FUNÇÕES PARA GERENCIAR AS CREDENCIAIS DE INTEGRAÇÃO ---

async def update_fuel_integration_settings(
    db: AsyncSession, *, db_obj: Organization, obj_in: OrganizationFuelIntegrationUpdate
) -> Organization:
    """
    Atualiza as configurações de integração de combustível,
    criptografando as chaves antes de salvar.
    """
    # Atualiza o nome do provedor diretamente
    if obj_in.fuel_provider_name is not None:
        db_obj.fuel_provider_name = obj_in.fuel_provider_name
    
    # Criptografa a chave de API se ela for fornecida
    if obj_in.fuel_provider_api_key is not None:
        db_obj.encrypted_fuel_provider_api_key = encrypt_data(obj_in.fuel_provider_api_key)

    # Criptografa o segredo da API se ele for fornecido
    if obj_in.fuel_provider_api_secret is not None:
        db_obj.encrypted_fuel_provider_api_secret = encrypt_data(obj_in.fuel_provider_api_secret)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


def get_decrypted_fuel_credentials(organization: Organization) -> dict:
    """
    Descriptografa e retorna as credenciais de combustível para uma organização.
    NÃO EXPONHA ESTA FUNÇÃO DIRETAMENTE NUMA API PÚBLICA.
    """
    return {
        "provider_name": organization.fuel_provider_name,
        "api_key": decrypt_data(organization.encrypted_fuel_provider_api_key),
        "api_secret": decrypt_data(organization.encrypted_fuel_provider_api_secret)
    }
