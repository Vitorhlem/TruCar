from app.db.base_class import Base
import os
import shutil

import app.models

from fastapi import FastAPI, Request, status, UploadFile, File, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.db.session import engine 

from app.core.logging_config import setup_logging
from fastapi.staticfiles import StaticFiles


# 1. Configurar o logging primeiro
setup_logging()

# 2. Criar a instância principal da aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Este handler intercepta os erros de validação 422 e traduz as mensagens.
    """
    errors = exc.errors()
    custom_errors = []
    for err in errors:
        new_err = err.copy() # Copia o erro original para não modificar o original
        if err['type'] == 'enum':
            # Traduz a mensagem de erro para Enums
            allowed_values = err['ctx']['expected']
            new_err['msg'] = f"O valor deve ser um dos seguintes: {allowed_values}"
        # Adicione outras traduções aqui se necessário
        # Ex: if err['type'] == 'string_too_short': new_err['msg'] = ...
        
        custom_errors.append(new_err)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": custom_errors},
    )


@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    """
    Recebe um arquivo de imagem, salva-o e retorna a URL pública.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="O arquivo não é uma imagem válida.")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{os.urandom(8).hex()}{file_extension}" # Gera um nome único
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar a imagem: {e}")

    # Retorna a URL completa da imagem. Adapte base_url conforme seu ambiente.
    # Em produção, você pode usar um CDN ou um servidor de arquivos estáticos.
    base_url = "https://trucar-api.onrender.com/" # URL do seu backend
    file_url = f"{base_url}/{UPLOAD_DIR}/{unique_filename}"

    return JSONResponse(content={"file_url": file_url})

# Servir arquivos estáticos (essencial para que as imagens salvas sejam acessíveis)
from fastapi.staticfiles import StaticFiles
app.mount(f"/{UPLOAD_DIR}", StaticFiles(directory=UPLOAD_DIR), name="static")
# 3. Adicionar o Middleware de CORS (logo após a criação do app)
origins = [
    "http://localhost",
    "http://localhost:9000",  # A origem do seu front-end Quasar em desenvolvimento
    # Adicione aqui outras origens se precisar (ex: o endereço do seu site em produção)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


app.mount("/static", StaticFiles(directory="static"), name="static")

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
app.include_router(api_router)
