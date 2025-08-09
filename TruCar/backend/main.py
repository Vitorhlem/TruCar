from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.db.session import engine 
from app.db.base_class import Base
from app.core.logging_config import setup_logging

# 1. Configurar o logging primeiro
setup_logging()

# 2. Criar a instância principal da aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 3. Adicionar o Middleware de CORS (logo após a criação do app)
origins = [
    "http://localhost:9000",
    "http://localhost:8080", # Porta alternativa do Quasar
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Adicionar o evento de startup para criar as tabelas
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 5. Adicionar a rota raiz
@app.get("/", status_code=200)
def read_root():
    """
    Endpoint raiz para verificar se a API está online.
    """
    return {"status": f"Welcome to {settings.PROJECT_NAME} API!", "version": "1.0.0"}

# 6. Incluir o roteador principal da API
app.include_router(api_router, prefix=settings.API_V1_STR)