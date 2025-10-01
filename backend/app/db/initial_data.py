import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base_class import Base
from app.core.config import settings

# Esta importação continua sendo essencial e está correta.
import app.models 

async def create_db_and_tables():
    """Apaga e recria todas as tabelas de forma robusta."""
    engine = create_async_engine(settings.DATABASE_URI)
    
    print("A apagar e recriar todas as tabelas...")
    async with engine.begin() as conn:
        # --- VOLTANDO À ABORDAGEM CASCADE ---
        # Esta é a forma mais eficaz de garantir uma limpeza total
        # e resolver o erro de dependência.
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        # --- FIM DA CORREÇÃO ---

        # Agora, recriamos todas as tabelas no schema limpo.
        await conn.run_sync(Base.metadata.create_all)
        
    print("Tabelas criadas com sucesso.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())