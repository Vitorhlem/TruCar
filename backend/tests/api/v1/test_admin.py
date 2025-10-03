# backend/tests/api/v1/test_admin.py

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.core import auth
from app.models.user_model import User, UserRole
from app.schemas.organization_schema import OrganizationCreate
from app.schemas.user_schema import UserCreate

@pytest.fixture
async def superuser_token_headers(client: AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    """
    Cria um super admin (se não existir) e retorna um cabeçalho de autorização para ele.
    """
    superuser_email = list(settings.SUPERUSER_EMAILS)[0]
    user = await crud.user.get_user_by_email(db=db_session, email=superuser_email)

    if not user:
        org = await crud.organization.create(
            db_session, 
            obj_in=OrganizationCreate(name="SuperAdmin Org", sector="servicos")
        )
        user_in = UserCreate(full_name="Test Super Admin", email=superuser_email, password="password")
        user = await crud.user.create(
            db_session, 
            user_in=user_in, 
            organization_id=org.id, 
            role=UserRole.CLIENTE_ATIVO
        )
    
    # CORREÇÃO: Usar o ID do utilizador (convertido para string) como o "subject" do token.
    access_token_jwt = auth.create_access_token(data={"sub": str(user.id)})
    
    return {"Authorization": f"Bearer {access_token_jwt}"}

# --- Testes (sem alterações a partir daqui) ---

@pytest.mark.asyncio
async def test_super_admin_can_list_organizations(client: AsyncClient, db_session: AsyncSession, superuser_token_headers: dict[str, str]):
    await crud.organization.create(db_session, obj_in=OrganizationCreate(name="Org A", sector="servicos", status="active"))
    await crud.organization.create(db_session, obj_in=OrganizationCreate(name="Org B", sector="frete", status="demo"))
    
    response = await client.get("/admin/organizations/", headers=superuser_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    organizations = response.json()
    assert len(organizations) >= 2

@pytest.mark.asyncio
async def test_super_admin_can_update_organization(client: AsyncClient, db_session: AsyncSession, superuser_token_headers: dict[str, str]):
    org = await crud.organization.create(db_session, obj_in=OrganizationCreate(name="Original Name", sector="agronegocio"))
    
    update_data = {"name": "Updated Name"}
    response = await client.put(f"/admin/organizations/{org.id}", json=update_data, headers=superuser_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    updated_org = response.json()
    assert updated_org["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_super_admin_can_activate_demo_user(client: AsyncClient, db_session: AsyncSession, superuser_token_headers: dict[str, str]):
    org = await crud.organization.create(db_session, obj_in=OrganizationCreate(name="Demo Org", sector="servicos"))
    user_in_schema = UserCreate(full_name="Demo User", email="demo@user.com", password="password")
    demo_user = await crud.user.create(db_session, user_in=user_in_schema, organization_id=org.id, role=UserRole.CLIENTE_DEMO)
    
    response = await client.post(f"/admin/users/{demo_user.id}/activate", headers=superuser_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    activated_user = response.json()
    assert activated_user["role"] == UserRole.CLIENTE_ATIVO.value

@pytest.mark.asyncio
async def test_super_admin_cannot_activate_non_demo_user(client: AsyncClient, db_session: AsyncSession, superuser_token_headers: dict[str, str]):
    org = await crud.organization.create(db_session, obj_in=OrganizationCreate(name="Driver Org", sector="frete"))
    user_in_schema = UserCreate(full_name="Driver User", email="driver@user.com", password="password")
    driver_user = await crud.user.create(db_session, user_in=user_in_schema, organization_id=org.id, role=UserRole.DRIVER)
    
    response = await client.post(f"/admin/users/{driver_user.id}/activate", headers=superuser_token_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_super_admin_can_impersonate_user(client: AsyncClient, db_session: AsyncSession, superuser_token_headers: dict[str, str]):
    org = await crud.organization.create(db_session, obj_in=OrganizationCreate(name="Target Org", sector="construcao_civil"))
    user_in_schema = UserCreate(full_name="Target User", email="target@user.com", password="password")
    target_user = await crud.user.create(db_session, user_in=user_in_schema, organization_id=org.id, role=UserRole.DRIVER)
    
    response = await client.post(f"/admin/users/{target_user.id}/impersonate", headers=superuser_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"