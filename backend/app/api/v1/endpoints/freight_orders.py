# ARQUIVO: backend/app/api/v1/endpoints/freight_orders.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.freight_order_schema import FreightOrderCreate, FreightOrderUpdate, FreightOrderPublic

router = APIRouter()

@router.post("/", response_model=FreightOrderPublic, status_code=status.HTTP_201_CREATED)
async def create_freight_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    freight_order_in: FreightOrderCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Cria uma nova ordem de frete com suas paradas (apenas para gestores).
    """
    # Validação extra: verificar se o cliente pertence à mesma organização
    client = await crud.client.get(db=db, id=freight_order_in.client_id, organization_id=current_user.organization_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente inválido ou não pertence a esta organização.")

    freight_order = await crud.freight_order.create_with_stops(
        db=db, obj_in=freight_order_in, organization_id=current_user.organization_id
    )
    return freight_order

@router.get("/", response_model=List[FreightOrderPublic])
async def read_freight_orders(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna uma lista de ordens de frete da organização do usuário.
    """
    freight_orders = await crud.freight_order.get_multi_by_org(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return freight_orders

@router.get("/{freight_order_id}", response_model=FreightOrderPublic)
async def read_freight_order_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    freight_order_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Busca uma ordem de frete específica pelo ID.
    """
    freight_order = await crud.freight_order.get(db=db, id=freight_order_id, organization_id=current_user.organization_id)
    if not freight_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de frete não encontrada.")
    return freight_order

@router.put("/{freight_order_id}", response_model=FreightOrderPublic)
async def update_freight_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    freight_order_id: int,
    freight_order_in: FreightOrderUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Atualiza uma ordem de frete, como alocar um veículo/motorista ou mudar o status.
    """
    db_freight_order = await crud.freight_order.get(db=db, id=freight_order_id, organization_id=current_user.organization_id)
    if not db_freight_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de frete não encontrada.")
    
    # Adicionar validações para vehicle_id e driver_id se necessário
    
    updated_freight_order = await crud.freight_order.update(db=db, db_obj=db_freight_order, obj_in=freight_order_in)
    return updated_freight_order