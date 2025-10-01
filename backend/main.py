# backend/main.py

import os
import shutil
from fastapi import FastAPI, Request, status, UploadFile, File, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importações da sua aplicação
import app.models
from app.api.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base_class import Base
from app.db.session import engine

# 1. Configurar o logging primeiro
setup_logging()

# 2. Definir constantes
UPLOAD_DIR = "static/uploads"  # Diretório para uploads dentro de 'static'

# 3. Criar a instância principal da aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/api/v1/openapi.json" # Mantém o openapi no prefixo para organização
)

# 4. Criar diretórios necessários
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 5. Adicionar o Middleware de CORS (logo após a criação do app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (ideal para mobile)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
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
    # ... (seu código de handler de exceção continua o mesmo, está ótimo)
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

# 8. Servir arquivos estáticos (só precisa de um mount)
# Isso fará com que o conteúdo da pasta 'static' seja acessível via URL
app.mount("/static", StaticFiles(directory="static"), name="static")


# 9. Endpoints específicos do main.py (como upload)
@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    """
    Recebe um arquivo de imagem, salva-o e retorna a URL pública.
    ATENÇÃO: Este método não é ideal para o Render. Veja a nota abaixo.
    """
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

    # A URL agora é relativa ao mount 'static'
    file_url = f"/static/uploads/{unique_filename}"
    
    return JSONResponse(content={"file_url": file_url})


# 10. Adicionar a rota raiz para verificação de status
@app.get("/", status_code=200, include_in_schema=False)
def read_root():
    return {"status": f"Welcome to {settings.PROJECT_NAME} API!"}

# 11. Incluir o roteador principal da API
app.include_router(api_router)