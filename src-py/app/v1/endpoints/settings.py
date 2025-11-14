from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, deps
from app.models.user_model import User
from app.schemas.organization_schema import (
    OrganizationFuelIntegrationUpdate,
    OrganizationFuelIntegrationPublic,
)

router = APIRouter()


@router.get("/fuel-integration", response_model=OrganizationFuelIntegrationPublic)
async def read_fuel_integration_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Obtém as configurações de integração de combustível da organização do usuário logado.
    Não retorna as chaves de API por segurança.
    """
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
    """
    Atualiza as configurações de integração de combustível da organização.
    As chaves são criptografadas antes de serem salvas.
    """
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