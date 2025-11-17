from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URI, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Função geradora para ser usada como uma Dependência do FastAPI.
    Este é o padrão CORRETO para gerenciamento de transação MANUAL,
    onde a rota é responsável por 'commit' e 'rollback'.
    """
    session: AsyncSession = SessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()