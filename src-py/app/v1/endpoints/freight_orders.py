
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, deps
from app.models.user_model import User, UserRole
from app.models.freight_order_model import FreightStatus
from app.models.journey_model import Journey
from app.schemas.freight_order_schema import (
    FreightOrderCreate, 
    FreightOrderUpdate, 
    FreightOrderPublic, 
    FreightOrderClaim,
    StopPointPublic
)
from app.schemas.journey_schema import JourneyPublic

router = APIRouter()



@router.post("/", response_model=FreightOrderPublic, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(deps.check_demo_limit("freight_orders"))])
async def create_freight_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    freight_order_in: FreightOrderCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """(Gestor) Cria uma nova ordem de frete com suas paradas."""
    client = await crud.client.get(db=db, id=freight_order_in.client_id, organization_id=current_user.organization_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente inválido.")

    freight_order = await crud.freight_order.create_with_stops(
        db=db, obj_in=freight_order_in, organization_id=current_user.organization_id
    )
    
    if current_user.role == UserRole.CLIENTE_DEMO:
        await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="freight_orders")
        
    return freight_order


@router.put("/{freight_order_id}", response_model=FreightOrderPublic)
async def update_freight_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    freight_order_id: int,
    freight_order_in: FreightOrderUpdate,
    current_user: User = Depends(deps.get_current_active_manager) # Protegido
):
    """(Gestor) Atualiza uma ordem de frete."""
    db_freight_order = await crud.freight_order.get(db=db, id=freight_order_id, organization_id=current_user.organization_id)
    if not db_freight_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de frete não encontrada.")
    
    updated_freight_order = await crud.freight_order.update(db=db, db_obj=db_freight_order, obj_in=freight_order_in)
    return updated_freight_order



@router.put("/{order_id}/claim", response_model=FreightOrderPublic)
async def claim_freight_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    order_id: int,
    claim_in: FreightOrderClaim,
    current_user: User = Depends(deps.get_current_active_user)
):
    """(Motorista) Permite que um motorista se atribua a um frete aberto."""
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas motoristas podem se atribuir a fretes.")

    order = await crud.freight_order.get(db, id=order_id, organization_id=current_user.organization_id)
    if not order:
        raise HTTPException(status_code=404, detail="Ordem de frete não encontrada.")
    
    vehicle = await crud.vehicle.get(db, vehicle_id=claim_in.vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    claimed_order = await crud.freight_order.claim_order(db, order=order, driver=current_user, vehicle=vehicle)
    return claimed_order


@router.post("/{order_id}/start-leg/{stop_point_id}", response_model=JourneyPublic)
async def start_journey_for_freight_stop(
    order_id: int,
    stop_point_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    (Motorista) Inicia a viagem para um ponto de parada específico.
    """
    order = await crud.freight_order.get(db, id=order_id, organization_id=current_user.organization_id)
    if not order or order.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Frete não encontrado ou não alocado a este motorista.")
    
    stop = next((s for s in order.stop_points if s.id == stop_point_id), None)
    if not stop:
        raise HTTPException(status_code=404, detail="Ponto de parada não encontrado neste frete.")
    
    if not order.vehicle:
        raise HTTPException(status_code=400, detail="Nenhum veículo alocado para este frete.")
        
    journey = await crud.freight_order.start_journey_for_stop(db, order=order, stop=stop, vehicle=order.vehicle)
    return journey


@router.put("/{order_id}/complete-stop/{stop_point_id}", response_model=StopPointPublic)
async def complete_freight_stop_point(
    order_id: int,
    stop_point_id: int,
    data: dict = Body(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    (Motorista) Marca um ponto de parada como concluído.
    Espera um body com: {"journey_id": int, "end_mileage": int}
    """
    order = await crud.freight_order.get(db, id=order_id, organization_id=current_user.organization_id)
    if not order or order.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Frete não alocado a este motorista.")

    stop = next((s for s in order.stop_points if s.id == stop_point_id), None)
    if not stop:
        raise HTTPException(status_code=404, detail="Ponto de parada não encontrado.")
    
    journey_id = data.get("journey_id")
    end_mileage = data.get("end_mileage")

    if journey_id is None or end_mileage is None:
        raise HTTPException(status_code=422, detail="Dados de finalização incompletos.")

    journey = await db.get(Journey, journey_id)
    if not journey or not journey.is_active or journey.freight_order_id != order_id:
        raise HTTPException(status_code=400, detail="Jornada ativa inválida para este frete.")

    completed_stop = await crud.freight_order.complete_stop_point(db, order=order, stop=stop, journey=journey, end_mileage=end_mileage)
    return completed_stop



@router.get("/", response_model=List[FreightOrderPublic])
async def read_freight_orders(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """(Gestor) Retorna a lista de todas as ordens de frete da organização."""
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(status_code=403, detail="Apenas gestores podem ver todas as ordens de frete.")
    
    freight_orders = await crud.freight_order.get_multi_by_org(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return freight_orders



@router.get("/open", response_model=List[FreightOrderPublic])
async def read_open_freight_orders(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    (Motorista) Retorna a lista de fretes abertos (mural).
    """
    open_orders = await crud.freight_order.get_multi_by_status(
        db, organization_id=current_user.organization_id, status=FreightStatus.OPEN
    )
    return open_orders


@router.get("/my-pending", response_model=List[FreightOrderPublic])
async def read_my_pending_freight_orders(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    (Motorista) Retorna a lista de fretes atribuídos ou em trânsito.
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
    (Todos) Busca uma ordem de frete específica pelo ID.
    """
    freight_order = await crud.freight_order.get(db=db, id=freight_order_id, organization_id=current_user.organization_id)
    if not freight_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de frete não encontrada.")
    return freight_order