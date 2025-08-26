import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# Garante que a base e as configurações sejam importadas
from app.db.base_class import Base
from app.core.config import settings
# Importa todos os seus modelos para que o SQLAlchemy os conheça
import app.models 

async def create_db_and_tables():
    """
    Apaga todas as tabelas e as recria do zero.
    PERIGO: ISTO APAGA TODOS OS DADOS. Use apenas em desenvolvimento.
    """
    # CORREÇÃO: Usamos DATABASE_URI, como sugerido pelo erro.
    engine = create_async_engine(settings.DATABASE_URI, echo=True)

    print("A apagar todas as tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Tabelas apagadas.")

    print("A criar todas as tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas criadas com sucesso.")
    
    await engine.dispose()

async def main():
    print("A iniciar o script de criação da base de dados...")
    await create_db_and_tables()
    print("Script finalizado.")

if __name__ == "__main__":
    asyncio.run(main())