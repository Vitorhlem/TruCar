from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging # <-- Adicionado para logs
import json # <-- Importar json para tratar exceções

from app import crud, deps
from app.db.session import SessionLocal
from app.models.user_model import User, UserRole
from app.models.notification_model import NotificationType
from app.schemas.fine_schema import FineCreate, FineUpdate, FinePublic

# Configuração do logger
logger = logging.getLogger(__name__)

# --- LOG DE INICIALIZAÇÃO ---
# Este log DEVE aparecer no console QUANDO O SERVIDOR INICIAR.
# Se ele não aparecer, o Uvicorn não está recarregando seus arquivos.
# --- FIM DO LOG DE INICIALIZAÇÃO ---


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


@router.post("/", response_model=FinePublic, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(deps.check_demo_limit("fines"))])
async def create_fine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    fine_in: FineCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Cria uma nova multa e notifica os gestores em segundo plano."""
    if current_user.role == UserRole.DRIVER and fine_in.driver_id != current_user.id:
        logger.warning(f"Tentativa FORBIDDEN de criar multa para outro driver. User: {current_user.id}, Tentativa: {fine_in.driver_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode registrar multas para si mesmo."
        )
          
    try:
        fine = await crud.fine.create(db=db, fine_in=fine_in, organization_id=current_user.organization_id)
        
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="fines")

        message = f"Nova multa de R${fine.value:.2f} registrada para o veículo."
        
        await db.flush()
        await db.refresh(fine)

        background_tasks.add_task(
            create_notification_background,
            message=message,
            notification_type=NotificationType.NEW_FINE_REGISTERED,
            organization_id=current_user.organization_id,
            send_to_managers=True,
            related_entity_type="fine",
            related_entity_id=fine.id,
            related_vehicle_id=fine.vehicle_id
        )
        
        await db.commit()
        await db.refresh(fine, ["vehicle", "driver", "cost"])
        
        return fine
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
    - Gestores veem todas as multas da organização.
    - Motoristas veem apenas as suas próprias multas.
    """
    try:
        if current_user.role in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
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
    request: Request, # <-- 3. Remover 'fine_in: FineUpdate' e adicionar 'request: Request'
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Atualiza uma multa existente e seu custo associado (Apenas Gestores)."""
    
    # --- 4. LER O JSON MANUALMENTE ---
    try:
        payload_dict = await request.json()
    except json.JSONDecodeError:
        logger.error(f"Erro ao ATUALIZAR multa ID {fine_id}: Payload não é um JSON válido.")
        raise HTTPException(status_code=400, detail="Payload JSON inválido.")
    
    # --- FIM DA LEITURA MANUAL ---

    try:
        db_fine = await crud.fine.get(db, fine_id=fine_id, organization_id=current_user.organization_id)
        if not db_fine:
            logger.error(f"Tentativa de update falhou: Multa ID {fine_id} não encontrada para a org {current_user.organization_id}")
            raise HTTPException(status_code=404, detail="Multa não encontrada.")
        
        
        # 5. Passar o dicionário 'payload_dict' para o CRUD
        fine = await crud.fine.update(db=db, db_fine=db_fine, fine_in_dict=payload_dict)
        
        await db.commit()
        
        await db.refresh(fine, ["vehicle", "driver", "cost"])
        
        return fine
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
            logger.error(f"Tentativa de delete falhou: Multa ID {fine_id} não encontrada para a org {current_user.organization_id}")
            raise HTTPException(status_code=404, detail="Multa não encontrada.")
        
        await crud.fine.remove(db=db, db_fine=db_fine)
        
        await db.commit()
        
        return
    except Exception as e:
        logger.error(f"Erro ao DELETAR multa ID {fine_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao deletar a multa.")