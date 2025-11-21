from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import logging
import json

from app import crud, deps
from app.db.session import SessionLocal
from app.models.user_model import User, UserRole
from app.models.fine_model import Fine
from app.models.notification_model import NotificationType
from app.schemas.fine_schema import FineCreate, FineUpdate, FinePublic

# Configuração do logger
logger = logging.getLogger(__name__)

router = APIRouter()

async def create_notification_background(
    message: str,
    notification_type: NotificationType,
    organization_id: int,
    send_to_managers: bool,
    related_entity_type: str,
    related_entity_id: int,
    related_vehicle_id: int | None
):
    db: AsyncSession | None = None
    try:
        async with SessionLocal() as db:
            await crud.notification.create_notification(
                db=db,
                message=message,
                notification_type=notification_type,
                organization_id=organization_id,
                send_to_managers=send_to_managers,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                related_vehicle_id=related_vehicle_id
            )
    except Exception as e:
        logger.error(f"ERRO na tarefa de background de notificação: {e}", exc_info=True)


@router.post("/", response_model=FinePublic, status_code=status.HTTP_201_CREATED)
async def create_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    fine_in: FineCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Cria uma nova multa e notifica os gestores em segundo plano."""
    
    if current_user.role == UserRole.DRIVER:
        fine_in.driver_id = current_user.id
          
    try:
        fine = await crud.fine.create(db=db, fine_in=fine_in, organization_id=current_user.organization_id)
        
        # Mantém o contador para estatísticas, mas SEM BLOQUEIO
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="fines")

        message = f"Nova multa de R${fine.value:.2f} registrada para o veículo."
        
        await db.flush()
        fine_id = fine.id 
        
        background_tasks.add_task(
            create_notification_background,
            message=message,
            notification_type=NotificationType.NEW_FINE_REGISTERED,
            organization_id=current_user.organization_id,
            send_to_managers=True,
            related_entity_type="fine",
            related_entity_id=fine_id,
            related_vehicle_id=fine.vehicle_id
        )
        
        await db.commit()
        
        stmt = (
            select(Fine)
            .where(Fine.id == fine_id)
            .options(
                selectinload(Fine.vehicle),
                selectinload(Fine.cost),
                selectinload(Fine.driver).selectinload(User.organization)
            )
        )
        result = await db.execute(stmt)
        fine_loaded = result.scalars().first()
        
        return fine_loaded
        
    except Exception as e:
        logger.error(f"Erro ao criar multa: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao salvar a multa.")
        
    except Exception as e:
        logger.error(f"Erro ao criar multa: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao salvar a multa.")

@router.get("/", response_model=List[FinePublic])
async def read_fines(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Lista as multas.
    """
    try:
        # CORREÇÃO 4: Adicionado ADMIN na lista de quem pode ver tudo
        if current_user.role in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO, UserRole.ADMIN]:
            fines = await crud.fine.get_multi_by_org(
                db, organization_id=current_user.organization_id, skip=skip, limit=limit
            )
        elif current_user.role == UserRole.DRIVER:
            fines = await crud.fine.get_multi_by_driver(
                db, driver_id=current_user.id, organization_id=current_user.organization_id, skip=skip, limit=limit
            )
        else:
            fines = []
        return fines
    except Exception as e:
        logger.error(f"Erro ao ler multas: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar multas.")


@router.put("/{fine_id}", response_model=FinePublic)
async def update_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    fine_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Atualiza uma multa existente e seu custo associado (Apenas Gestores)."""
    
    try:
        payload_dict = await request.json()
    except json.JSONDecodeError:
        logger.error(f"Erro ao ATUALIZAR multa ID {fine_id}: Payload não é um JSON válido.")
        raise HTTPException(status_code=400, detail="Payload JSON inválido.")
    
    try:
        db_fine = await crud.fine.get(db, fine_id=fine_id, organization_id=current_user.organization_id)
        if not db_fine:
            raise HTTPException(status_code=404, detail="Multa não encontrada.")
        
        await crud.fine.update(db=db, db_fine=db_fine, fine_in_dict=payload_dict)
        
        await db.commit()
        
        # Mesma lógica de recarregamento seguro usada no create
        stmt = (
            select(Fine)
            .where(Fine.id == fine_id)
            .options(
                selectinload(Fine.vehicle),
                selectinload(Fine.cost),
                selectinload(Fine.driver).selectinload(User.organization)
            )
        )
        result = await db.execute(stmt)
        fine_loaded = result.scalars().first()
        
        return fine_loaded
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao ATUALIZAR multa ID {fine_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao atualizar a multa.")

@router.delete("/{fine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    fine_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Deleta uma multa e seu custo associado (Apenas Gestores)."""
    try:
        db_fine = await crud.fine.get(db, fine_id=fine_id, organization_id=current_user.organization_id)
        if not db_fine:
            raise HTTPException(status_code=404, detail="Multa não encontrada.")
        
        await crud.fine.remove(db=db, db_fine=db_fine)
        
        await db.commit()
        
        return
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao DELETAR multa ID {fine_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao deletar a multa.")