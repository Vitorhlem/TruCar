from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import shutil
from pathlib import Path

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.part_schema import PartPublic, PartCreate, PartUpdate

router = APIRouter()

UPLOAD_DIRECTORY = Path("static/uploads/parts")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIRECTORY / unique_filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return f"/static/uploads/parts/{unique_filename}"

@router.post("/", response_model=PartPublic, status_code=status.HTTP_201_CREATED)
async def create_part(
    db: AsyncSession = Depends(deps.get_db),
    name: str = Form(...),
    part_number: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    stock: int = Form(...),
    min_stock: int = Form(...),
    location: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Cria uma nova peça no inventário."""
    part_in = PartCreate(
        name=name, part_number=part_number, brand=brand, stock=stock,
        min_stock=min_stock, location=location, notes=notes
    )
    
    photo_url = None
    if file:
        photo_url = await save_upload_file(file)
    
    part_db = await crud.part.create(
        db=db, part_in=part_in, organization_id=current_user.organization_id, photo_url=photo_url
    )
    return part_db

@router.put("/{part_id}", response_model=PartPublic)
async def update_part(
    part_id: int,
    db: AsyncSession = Depends(deps.get_db),
    name: str = Form(...),
    part_number: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    stock: int = Form(...),
    min_stock: int = Form(...),
    location: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Atualiza uma peça no inventário."""
    db_part = await crud.part.get(db, id=part_id, organization_id=current_user.organization_id)
    if not db_part:
        raise HTTPException(status_code=404, detail="Peça não encontrada.")
        
    part_in = PartUpdate(
        name=name, part_number=part_number, brand=brand, stock=stock,
        min_stock=min_stock, location=location, notes=notes
    )
    
    photo_url = db_part.photo_url
    if file:
        photo_url = await save_upload_file(file)
    
    updated_part = await crud.part.update(
        db=db, db_obj=db_part, obj_in=part_in, photo_url=photo_url
    )
    return updated_part

@router.get("/", response_model=List[PartPublic])
async def read_parts(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Retorna a lista de peças do inventário."""
    parts = await crud.part.get_multi_by_org(
        db, organization_id=current_user.organization_id, search=search, skip=skip, limit=limit
    )
    return parts

@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Remove uma peça do inventário."""
    db_part = await crud.part.get(db, id=part_id, organization_id=current_user.organization_id)
    if not db_part:
        raise HTTPException(status_code=404, detail="Peça não encontrada.")
    await crud.part.remove(db=db, id=part_id)

