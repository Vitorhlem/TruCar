from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.core.config import settings

# Cria o "motor" (engine) de conexão com o banco de dados.
engine = create_async_engine(settings.DATABASE_URI, pool_pre_ping=True)

# Cria uma "fábrica" de sessões.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession,
    # --- CORREÇÃO AQUI ---
    # Impede que os objetos expirem após o commit. 
    # Isso é CRUCIAL para evitar erros de 'MissingGreenlet' ao acessar 
    # atributos de objetos (como current_user) depois de um commit na mesma rota.
    expire_on_commit=False
    # ---------------------
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Função geradora para ser usada como uma Dependência do FastAPI.
    Este é o padrão CORRETO para gerenciamento de transação MANUAL,
    onde a rota é responsável por 'commit' e 'rollback'.
    """
    session: AsyncSession = SessionLocal()
    try:
        # Entrega a sessão para a rota
        yield session
    except Exception:
        # Se um erro na rota não for tratado, desfazemos (rollback)
        await session.rollback()
        raise
    finally:
        # Garante que a sessão seja fechada ao final da requisição
        await session.close()
