# backend/main.py

import os
import shutil
from fastapi import FastAPI, Request, status, UploadFile, File, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importações da sua aplicação
from app.api.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import engine

# ======================= BLOCO DE IMPORTAÇÃO DOS MODELOS =======================
# A LINHA MÁGICA: Importa a Base e todos os modelos ANTES do startup.
# Isto garante que a Base já conheça todas as suas tabelas quando
# a função on_startup for chamada para criá-las.
from app.db.base_class import Base
from app.models.organization_model import Organization
from app.models.user_model import User
from app.models.vehicle_model import Vehicle
from app.models.implement_model import Implement
from app.models.part_model import Part
from app.models.client_model import Client
from app.models.freight_order_model import FreightOrder
from app.models.stop_point_model import StopPoint
from app.models.journey_model import Journey
from app.models.maintenance_model import MaintenanceRequest, MaintenanceComment
from app.models.fuel_log_model import FuelLog
from app.models.notification_model import Notification
from app.models.location_history_model import LocationHistory
from app.models.achievement_model import Achievement, UserAchievement
from app.models.inventory_transaction_model import InventoryTransaction
from app.models.document_model import Document
from app.models.goal_model import Goal
from app.models.alert_model import Alert
from app.models.vehicle_cost_model import VehicleCost
from app.models.vehicle_component_model import VehicleComponent
from app.models.tire_model import VehicleTire # Importa o novo modelo de pneu

# ==============================================================================


# 1. Configurar o logging primeiro
setup_logging()

# 2. Definir constantes
UPLOAD_DIR = "static/uploads"

# 3. Criar a instância principal da aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 4. Criar diretórios necessários
os.makedirs(UPLOAD_DIR, exist_ok=True)

origins = [
    "https://trucar-api.onrender.com",  # A URL do seu front-end em produção
    "http://localhost",
    "http://localhost:8080", # Porta padrão do Quasar em desenvolvimento
    "http://localhost:9000", # Outra porta comum do Quasar
    # Adicione outras URLs se necessário
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# 6. Adicionar o evento de startup para criar as tabelas
@app.on_event("startup")
async def on_startup():
    """
    Cria as tabelas no banco de dados na inicialização da aplicação.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 7. Adicionar Handlers de Exceção
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Este handler intercepta os erros de validação 422 e traduz as mensagens.
    """
    errors = exc.errors()
    custom_errors = []
    for err in errors:
        new_err = err.copy()
        if err['type'] == 'enum':
            allowed_values = err['ctx']['expected']
            new_err['msg'] = f"O valor deve ser um dos seguintes: {allowed_values}"
        custom_errors.append(new_err)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": custom_errors},
    )

# 8. Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


# 9. Endpoint de Upload (Aviso: temporário no Render)
@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="O arquivo não é uma imagem válida.")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{os.urandom(8).hex()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar a imagem: {e}")

    file_url = f"/static/uploads/{unique_filename}"
    return JSONResponse(content={"file_url": file_url})

# 10. Adicionar a rota raiz para verificação de status
@app.get("/", status_code=200, include_in_schema=False)
def read_root():
    return {"status": f"Welcome to {settings.PROJECT_NAME} API!"}

# 11. Incluir o roteador principal da API
# Lembre-se que removemos o prefixo para funcionar corretamente no Render
app.include_router(api_router)