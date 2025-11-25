# backend/main.py
import io
from PIL import Image
import os
import shutil
from fastapi import FastAPI, Request, status, UploadFile, File, HTTPException
from fastapi.exceptions import RequestValidationError, HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importações da sua aplicação
from app.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import engine

# ======================= BLOCO DE IMPORTAÇÃO DOS MODELOS =======================
# Este bloco garante que a Base do SQLAlchemy conheça todas as suas tabelas
# antes que a função on_startup seja chamada para criá-las.

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
from app.models.tire_model import VehicleTire
from app.models.fine_model import Fine
from app.models.feedback_model import Feedback
# --- ESTA É A CORREÇÃO DEFINITIVA ---
# Adiciona o nosso novo modelo à lista de modelos conhecidos.
from app.models.demo_usage_model import DemoUsage
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

# 5. Configurar o CORS
origins = [
    "https://trucar.netlify.app",    # Frontend em Produção (Netlify)
    "http://localhost",               # Localhost padrão
    "http://localhost:8080",          # Quasar/Vue padrão (se estiver usando)
    "http://localhost:9000",          # Quasar/Vue Dev padrão
]   

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Agora especifica a origem exata
    allow_credentials=True,           # Permite credenciais (necessário para Bearer tokens)
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Adicionar o evento de startup para criar as tabelas
@app.on_event("startup")
async def on_startup():
    """
    Cria as tabelas no banco de dados na inicialização da aplicação.
    """
    async with engine.begin() as conn:
        # Agora, Base.metadata.create_all conhece a tabela 'organization'
        # e a 'demousage', e as criará na ordem correta.
        await conn.run_sync(Base.metadata.create_all)

# 7. Adicionar Handlers de Exceção
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    custom_errors = []
    for err in errors:
        new_err = err.copy()
        
        # CORREÇÃO: Remove ou converte campos 'input' que sejam bytes
        # pois json.dumps não consegue serializar bytes.
        if 'input' in new_err and isinstance(new_err['input'], bytes):
            new_err['input'] = "Binary data (files or multipart form)"
            
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

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 413:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Arquivo muito grande. O limite máximo é de 5MB."},
        )
    # Mantém o comportamento padrão para outras exceções HTTP
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# 9. Endpoint de Upload
@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(..., max_size=5 * 1024 * 1024)): # Limite de 5MB
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="O arquivo não é uma imagem válida.")

    # --- Validação de conteúdo com Pillow ---
    try:
        # Lê o conteúdo do arquivo para um buffer de memória
        contents = await file.read()
        # Tenta abrir o buffer com o Pillow
        img = Image.open(io.BytesIO(contents))
        img.verify() # Verifica a integridade dos dados da imagem
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao processar. O arquivo pode estar corrompido ou não é uma imagem válida.")
    # --- Fim da validação ---

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{os.urandom(8).hex()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # Salva o conteúdo 'contents' que já lemos e validamos
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar a imagem: {e}")

    file_url = f"/static/uploads/{unique_filename}"
    return JSONResponse(content={"file_url": file_url})

# 10. Adicionar a rota raiz para verificação de status
@app.get("/", status_code=200, include_in_schema=False)
def read_root():
    return {"status": f"Welcome to {settings.PROJECT_NAME} API!"}

# 11. Incluir o roteador principal da API
app.include_router(api_router)