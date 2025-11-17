
import pytest # Importe o pytest
from fastapi import status
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    """
        Testa se o endpoint raiz da aplicação responde com o status 200 (OK)
        e com a mensagem de boas-vindas esperada.
    """
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "status" in json_response
    assert "Welcome to TruCar API!" in json_response["status"]