# backend/tests/api/v1/test_clients.py

import pytest
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core import auth
from app.models.user_model import UserRole
from app.schemas.organization_schema import OrganizationCreate
from app.schemas.user_schema import UserCreate
from app.schemas.client_schema import ClientCreate

# --- Fixtures de Autenticação para Testes ---

@pytest.fixture
async def manager_user_token_headers(db_session: AsyncSession) -> tuple[dict[str, str], int]:
    unique_id = uuid.uuid4().hex[:6]
    org = await crud.organization.create(db_session, obj_in=OrganizationCreate(name=f"Manager Org {unique_id}", sector="servicos"))
    user_in = UserCreate(full_name=f"Test Manager {unique_id}", email=f"manager_{unique_id}@test.com", password="password")
    manager_user = await crud.user.create(db_session, user_in=user_in, organization_id=org.id, role=UserRole.CLIENTE_ATIVO)
    
    token = auth.create_access_token(data={"sub": str(manager_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    return headers, org.id

@pytest.fixture
async def driver_user_token_headers(db_session: AsyncSession) -> tuple[dict[str, str], int]:
    unique_id = uuid.uuid4().hex[:6]
    org = await crud.organization.create(db_session, obj_in=OrganizationCreate(name=f"Driver Org {unique_id}", sector="frete"))
    user_in = UserCreate(full_name=f"Test Driver {unique_id}", email=f"driver_{unique_id}@test.com", password="password")
    driver_user = await crud.user.create(db_session, user_in=user_in, organization_id=org.id, role=UserRole.DRIVER)
    
    token = auth.create_access_token(data={"sub": str(driver_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    return headers, org.id

# --- Testes para o Endpoint de Clientes ---

@pytest.mark.asyncio
async def test_manager_can_create_client(client: AsyncClient, manager_user_token_headers: tuple[dict[str, str], int]):
    headers, org_id = manager_user_token_headers
    client_data = {"name": "New Client Inc.", "contact_person": "John Doe", "contact_email": "john.doe@client.com"}
    
    response = await client.post("/clients/", json=client_data, headers=headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == client_data["name"]

@pytest.mark.asyncio
async def test_driver_cannot_create_client(client: AsyncClient, driver_user_token_headers: tuple[dict[str, str], int]):
    headers, org_id = driver_user_token_headers
    
    response = await client.post("/clients/", json={"name": "Unauthorized Client"}, headers=headers)
    
    # Com a correção em deps.py, este teste agora deve passar
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_user_can_read_clients_from_own_org(
    client: AsyncClient, db_session: AsyncSession, manager_user_token_headers: tuple[dict[str, str], int]
):
    headers, org_id = manager_user_token_headers
    await crud.client.create(db_session, obj_in=ClientCreate(name="Client A"), organization_id=org_id)
    
    response = await client.get("/clients/", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Client A"

@pytest.mark.asyncio
async def test_manager_can_update_client(
    client: AsyncClient, db_session: AsyncSession, manager_user_token_headers: tuple[dict[str, str], int]
):
    headers, org_id = manager_user_token_headers
    client_obj = await crud.client.create(db_session, obj_in=ClientCreate(name="Original Name"), organization_id=org_id)
    
    update_data = {"name": "Updated Name"}
    # O URL correto para o endpoint de clientes
    response = await client.put(f"/clients/{client_obj.id}", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_manager_can_delete_client(
    client: AsyncClient, db_session: AsyncSession, manager_user_token_headers: tuple[dict[str, str], int]
):
    headers, org_id = manager_user_token_headers
    client_obj = await crud.client.create(db_session, obj_in=ClientCreate(name="To Be Deleted"), organization_id=org_id)
    
    # O URL correto para o endpoint de clientes
    response = await client.delete(f"/clients/{client_obj.id}", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    
    deleted_client = await crud.client.get(db_session, id=client_obj.id, organization_id=org_id)
    assert deleted_client is None