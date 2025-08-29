# ARQUIVO: backend/app/api/v1/endpoints/freight_orders.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.journey_schema import JourneyPublic # Adicione este import

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.freight_order_schema import FreightOrderCreate, FreightOrderUpdate, FreightOrderPublic, StopPointPublic, FreightOrderClaim, FreightStatus


router = APIRouter()

@router.get("/open", response_model=List[FreightOrderPublic])
async def read_open_freight_orders(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna a lista de fretes abertos (mural do motorista).
    """
    # Precisaremos de uma nova função no CRUD para isso
    open_orders = await crud.freight_order.get_multi_by_status(
        db, organization_id=current_user.organization_id, status=FreightStatus.OPEN
    )
    return open_orders

@router.put("/{order_id}/claim", response_model=FreightOrderPublic)
async def claim_freight_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    order_id: int,
    claim_in: FreightOrderClaim, # O motorista envia o ID do veículo que ele escolheu
    current_user: User = Depends(deps.get_current_active_user) # Deve ser um motorista
):
    """
    Permite que um motorista se atribua a um frete aberto.
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas motoristas podem se atribuir a fretes.")

    # Busca a ordem de frete
    order = await crud.freight_order.get(db, id=order_id, organization_id=current_user.organization_id)
    if not order:
        raise HTTPException(status_code=404, detail="Ordem de frete não encontrada.")
    
    # Busca o veículo que o motorista selecionou
    vehicle = await crud.vehicle.get(db, vehicle_id=claim_in.vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    # Chama a função do CRUD que contém a lógica de negócio
    claimed_order = await crud.freight_order.claim_order(db, order=order, driver=current_user, vehicle=vehicle)
    return claimed_order


@router.post("/{order_id}/start-leg/{stop_point_id}", response_model=JourneyPublic)
async def start_journey_for_freight_stop(
    order_id: int,
    stop_point_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Inicia a viagem para um ponto de parada específico."""
    order = await crud.freight_order.get(db, id=order_id, organization_id=current_user.organization_id)
    if not order or order.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Frete não encontrado ou não alocado a este motorista.")
    
    stop = next((s for s in order.stop_points if s.id == stop_point_id), None)
    if not stop:
        raise HTTPException(status_code=404, detail="Ponto de parada não encontrado neste frete.")
        
    # Adicione mais validações aqui (ex: o veículo está disponível?)
    
    journey = await crud.freight_order.start_journey_for_stop(db, order=order, stop=stop, vehicle=order.vehicle)
    return journey

@router.put("/{order_id}/complete-stop/{stop_point_id}", response_model=StopPointPublic)
async def complete_freight_stop_point(
    order_id: int,
    stop_point_id: int,
    end_mileage: int, # O motorista informará o KM final
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Marca um ponto de parada como concluído."""
    order = await crud.freight_order.get(db, id=order_id, organization_id=current_user.organization_id)
    # ... (validações similares à rota anterior)

    stop = next((s for s in order.stop_points if s.id == stop_point_id), None)
    # ... (validações)
    
    # Encontra a Journey ativa para este frete
    active_journey = next((j for j in order.journeys if j.is_active), None)
    if not active_journey:
        raise HTTPException(status_code=400, detail="Nenhuma viagem ativa encontrada para este frete.")

    completed_stop = await crud.freight_order.complete_stop_point(db, order=order, stop=stop, journey=active_journey, end_mileage=end_mileage)
    return completed_stop

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

@router.get("/my-pending", response_model=List[FreightOrderPublic])
async def read_my_pending_freight_orders(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user) # Qualquer usuário logado pode ver suas tarefas
):
    """
    Retorna a lista de fretes pendentes ou em trânsito para o motorista logado.
    """
    freight_orders = await crud.freight_order.get_pending_by_driver(
        db, driver_id=current_user.id, organization_id=current_user.organization_id
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