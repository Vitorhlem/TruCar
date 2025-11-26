from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, deps
from app.models.user_model import User, UserRole
from app.schemas.organization_schema import (
    OrganizationFuelIntegrationUpdate,
    OrganizationFuelIntegrationPublic,
    OrganizationUpdate,
    OrganizationPublic
)

router = APIRouter()

# --- ENDPOINTS DE ORGANIZAÇÃO ---

@router.get("/organization", response_model=OrganizationPublic)
async def read_organization_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager), # Aceita Admin, Ativo e Demo
):
    """
    Retorna os dados da organização do usuário atual.
    """
    organization = await crud.organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada.")
    return organization

@router.put("/organization", response_model=OrganizationPublic)
async def update_organization_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    org_in: OrganizationUpdate,
    current_user: User = Depends(deps.get_current_active_manager), # Aceita Admin, Ativo e Demo
):
    """
    Atualiza as configurações da organização (Nome, CNPJ, Setor, etc).
    Totalmente liberado para CLIENTE_DEMO para facilitar testes.
    """
    organization = await crud.organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada.")

    # Atualiza no banco
    updated_org = await crud.organization.update(
        db=db, db_obj=organization, obj_in=org_in
    )

    return updated_org

# --- ENDPOINTS DE INTEGRAÇÃO DE COMBUSTÍVEL ---

@router.get("/fuel-integration", response_model=OrganizationFuelIntegrationPublic)
async def read_fuel_integration_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    organization = await crud.organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada.")

    return OrganizationFuelIntegrationPublic(
        fuel_provider_name=organization.fuel_provider_name,
        is_api_key_set=bool(organization.encrypted_fuel_provider_api_key),
        is_api_secret_set=bool(organization.encrypted_fuel_provider_api_secret),
    )


@router.put("/fuel-integration", response_model=OrganizationFuelIntegrationPublic)
async def update_fuel_integration_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    settings_in: OrganizationFuelIntegrationUpdate,
    current_user: User = Depends(deps.get_current_active_manager),
):
    organization = await crud.organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada.")

    updated_org = await crud.organization.update_fuel_integration_settings(
        db=db, db_obj=organization, obj_in=settings_in
    )

    return OrganizationFuelIntegrationPublic(
        fuel_provider_name=updated_org.fuel_provider_name,
        is_api_key_set=bool(updated_org.encrypted_fuel_provider_api_key),
        is_api_secret_set=bool(updated_org.encrypted_fuel_provider_api_secret),
    )