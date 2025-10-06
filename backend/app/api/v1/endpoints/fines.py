# Em backend/app/api/v1/endpoints/fines.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.fine_schema import FineCreate, FineUpdate, FinePublic

router = APIRouter()

@router.post("/", response_model=FinePublic, status_code=status.HTTP_201_CREATED)
async def create_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    fine_in: FineCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Cria uma nova multa para a organização."""
    # Validações (ex: verificar se veículo e motorista existem) podem ser adicionadas no CRUD
    fine = await crud.fine.create(db=db, fine_in=fine_in, organization_id=current_user.organization_id)
    return fine

@router.get("/", response_model=List[FinePublic])
async def read_fines(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Lista todas as multas da organização."""
    fines = await crud.fine.get_multi_by_org(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return fines

@router.put("/{fine_id}", response_model=FinePublic)
async def update_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    fine_id: int,
    fine_in: FineUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Atualiza uma multa existente."""
    db_fine = await crud.fine.get(db, fine_id=fine_id, organization_id=current_user.organization_id)
    if not db_fine:
        raise HTTPException(status_code=404, detail="Multa não encontrada.")
    
    fine = await crud.fine.update(db=db, db_fine=db_fine, fine_in=fine_in)
    return fine

@router.delete("/{fine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    fine_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Deleta uma multa."""
    db_fine = await crud.fine.get(db, fine_id=fine_id, organization_id=current_user.organization_id)
    if not db_fine:
        raise HTTPException(status_code=404, detail="Multa não encontrada.")
    
    await crud.fine.remove(db=db, db_fine=db_fine)