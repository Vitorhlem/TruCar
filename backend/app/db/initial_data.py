import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base_class import Base
from app.core.config import settings
import app.models 

async def create_db_and_tables():
    """Apaga e recria todas as tabelas."""
    engine = create_async_engine(settings.DATABASE_URI)
    print("A apagar e recriar todas as tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas criadas com sucesso.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())