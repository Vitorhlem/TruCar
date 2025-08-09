from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.core.config import settings

# Cria o "motor" (engine) de conexão com o banco de dados.
# O engine gerencia um pool de conexões para otimizar a performance,
# evitando o custo de abrir e fechar uma nova conexão a cada consulta.
# Usamos um engine assíncrono para alta performance com FastAPI.
engine = create_async_engine(settings.DATABASE_URI, pool_pre_ping=True)

# Cria uma "fábrica" de sessões.
# A partir daqui, vamos gerar sessões individuais para cada transação.
# autocommit=False e autoflush=False são as configurações padrão e seguras
# para usar o ORM do SQLAlchemy em uma aplicação web.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Função geradora para ser usada como uma Dependência do FastAPI.

    Ela gerencia o ciclo de vida de uma sessão com o banco de dados:
    1. Cria uma nova sessão para uma única requisição da API.
    2. "Entrega" (yield) essa sessão para a função da rota que a solicitou.
    3. Garante que a sessão seja fechada ao final da requisição,
       mesmo que um erro tenha ocorrido.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()