from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import shutil
from pathlib import Path

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.document_schema import DocumentPublic, DocumentCreate, DocumentUpdate
from app.models.document_model import DocumentType

router = APIRouter()

# Define o diretório de uploads
UPLOAD_DIRECTORY = Path("static/uploads/documents")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


async def save_upload_file(upload_file: UploadFile) -> str:
    """Salva um arquivo de upload e retorna sua URL pública."""
    # Gera um nome de arquivo único para evitar conflitos
    extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIRECTORY / unique_filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    # Retorna a URL relativa que o frontend pode usar
    return f"/static/uploads/documents/{unique_filename}"


@router.post("/", response_model=DocumentPublic, status_code=status.HTTP_201_CREATED)
async def create_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    # Usamos Form() para receber os dados do formulário junto com o arquivo
    document_type: DocumentType = Form(...),
    expiry_date: date = Form(...),
    notes: str = Form(None),
    vehicle_id: int = Form(None),
    driver_id: int = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Cria um novo documento, incluindo o upload do arquivo.
    Acessível apenas por gestores.
    """
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gestores podem criar documentos."
        )

    # Cria o objeto Pydantic com os dados do formulário
    document_in = DocumentCreate(
        document_type=document_type,
        expiry_date=expiry_date,
        notes=notes,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
    )

    file_url = await save_upload_file(file)

    created_document = await crud.document.create_with_file_url(
        db=db,
        obj_in=document_in,
        organization_id=current_user.organization_id,
        file_url=file_url
    )
    return created_document


@router.get("/", response_model=List[DocumentPublic])
async def read_documents(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    expiring_in_days: int = None,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Lista os documentos da organização, com filtros opcionais.
    """
    documents = await crud.document.get_multi_by_org(
        db=db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        expiring_in_days=expiring_in_days
    )
    return documents


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    doc_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Remove um documento. Acessível apenas por gestores.
    """
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gestores podem remover documentos."
        )

    doc_to_delete = await crud.document.get(db, id=doc_id, organization_id=current_user.organization_id)
    if not doc_to_delete:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")

    # Tenta apagar o arquivo físico
    try:
        file_path_str = doc_to_delete.file_url.lstrip("/")
        file_path = Path(file_path_str)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Erro ao apagar arquivo físico: {e}")

    await crud.document.remove(db, id=doc_id, organization_id=current_user.organization_id)
    return
