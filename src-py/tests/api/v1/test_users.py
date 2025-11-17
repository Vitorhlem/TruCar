
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.user_model import User, UserRole
from app import deps
from app.db.base_class import Base
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db?cache=shared"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

def override_get_current_active_manager():
    return User(
        id=1,
        email="manager@test.com",
        role=UserRole.CLIENTE_ATIVO,
        is_active=True,
        organization_id=1  # Associa o manager à organização de teste
    )

app.dependency_overrides[deps.get_db] = override_get_db
app.dependency_overrides[deps.get_current_active_manager] = override_get_current_active_manager



@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fornece uma sessão de base de dados limpa para cada teste.
    As alterações são desfeitas no final.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac