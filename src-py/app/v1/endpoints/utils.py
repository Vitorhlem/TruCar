import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Path as FastApiPath
import httpx

router = APIRouter()


UPLOAD_DIRECTORY = Path("static/uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

@router.post("/upload-photo", response_model=dict)
async def upload_photo(file: UploadFile = File(...)):
    """
    Recebe um ficheiro de imagem, valida, guarda-o localmente com um nome único
    e retorna a URL de acesso público.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/avif"]:
        raise HTTPException(status_code=400, detail="Tipo de ficheiro de imagem inválido. Apenas JPG, PNG, WEBP e AVIF são permitidos.")

    try:
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = UPLOAD_DIRECTORY / unique_filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"file_url": f"/{file_path}"}
    except Exception as e:
        print(f"Erro durante o upload do ficheiro: {e}")
        raise HTTPException(status_code=500, detail="Não foi possível guardar o ficheiro.")



@router.get("/cep/{cep}")
async def get_address_by_cep(
    cep: str = FastApiPath(..., title="O CEP para consulta", regex="^[0-9]{8}$")
):
    """
    Consulta um CEP no serviço ViaCEP e retorna os dados do endereço.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
            response.raise_for_status()
            
            data = response.json()
            if data.get("erro"):
                raise HTTPException(status_code=404, detail="CEP não encontrado.")
            
            return {
                "street": data.get("logradouro"),
                "neighborhood": data.get("bairro"),
                "city": data.get("localidade"),
                "state": data.get("uf"),
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Erro ao consultar o serviço de CEP.")
        except Exception:
            raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação de CEP.")
