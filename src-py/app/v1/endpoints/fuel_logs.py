from fastapi import APIRouter, Depends, status, HTTPException, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.models.notification_model import NotificationType
from app import crud, deps
from app.models.user_model import User, UserRole
from app.schemas.fuel_log_schema import FuelLogPublic, FuelLogCreate, FuelLogUpdate

router = APIRouter()

@router.post("/", response_model=FuelLogPublic, status_code=status.HTTP_201_CREATED)
async def create_fuel_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    log_in: FuelLogCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Cria um novo registro de abastecimento (Motoristas e Gestores)."""
    
    if current_user.role == UserRole.CLIENTE_DEMO:
        pass

    final_user_id = log_in.user_id if log_in.user_id else current_user.id

    fuel_log = await crud.fuel_log.create_fuel_log(
        db, 
        log_in=log_in, 
        user_id=final_user_id, 
        organization_id=current_user.organization_id
    )
    
    if current_user.role == UserRole.CLIENTE_DEMO:
        await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="fuel_logs")
        
    # --- ADIÇÃO DE LOG DE AUDITORIA (Recomendado, já que você tem o sistema) ---
    try:
        from app.schemas.audit_log_schema import AuditLogCreate
        from app.crud import crud_audit_log
        
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="CREATE", resource_type="Registro de Abastecimento", resource_id=str(fuel_log.id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"liters": fuel_log.liters, "cost": fuel_log.total_cost, "vehicle_id": fuel_log.vehicle_id}
        ))
        await db.commit()
    except Exception:
        pass # Não trava o fluxo principal se o log falhar
    # ---------------------------------------------------------------------------

    vehicle = await crud.vehicle.get(
        db, 
        vehicle_id=fuel_log.vehicle_id, 
        organization_id=current_user.organization_id
    )
    
    if vehicle:
        is_abnormal, details = await crud.fuel_log.check_abnormal_consumption(db, fuel_log=fuel_log, vehicle=vehicle)
        if is_abnormal:
            background_tasks.add_task(
                crud.notification.create_notification,
                db=db, message=details, notification_type=NotificationType.ABNORMAL_FUEL_CONSUMPTION,
                organization_id=current_user.organization_id, send_to_managers=True,
                related_entity_type="fuel_log", related_entity_id=fuel_log.id,
                related_vehicle_id=vehicle.id
            )
    return fuel_log


@router.get("/", response_model=List[FuelLogPublic])
async def read_fuel_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retorna o histórico de abastecimentos."""
    # --- CORREÇÃO AQUI: Adicionado UserRole.ADMIN ---
    # Se for Admin ou Cliente, vê TUDO da organização.
    if current_user.role in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO, UserRole.ADMIN]:
        return await crud.fuel_log.get_multi_by_org(
            db=db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
    else: 
        # DRIVER vê apenas os seus
        return await crud.fuel_log.get_multi_by_user(
            db=db, user_id=current_user.id, organization_id=current_user.organization_id, skip=skip, limit=limit
        )

@router.get("/{log_id}", response_model=FuelLogPublic)
async def read_fuel_log_by_id(
    log_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    log = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not log:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    return log

@router.put("/{log_id}", response_model=FuelLogPublic)
async def update_fuel_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    log_id: int,
    log_in: FuelLogUpdate,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Atualiza um registro de abastecimento (Apenas Gestores)."""
    db_log = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    
    updated_log = await crud.fuel_log.update_fuel_log(db=db, db_obj=db_log, obj_in=log_in)
    
    # --- AUDITORIA ---
    try:
        from app.schemas.audit_log_schema import AuditLogCreate
        from app.crud import crud_audit_log
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="UPDATE", resource_type="Registro de Abastecimento", resource_id=str(log_id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details=log_in.model_dump(exclude_unset=True)
        ))
        await db.commit()
    except Exception:
        pass
    # -----------------

    return updated_log

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fuel_log(
    log_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Exclui um registro de abastecimento (Apenas Gestores)."""
    log_to_delete = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not log_to_delete:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    
    # Guarda dados para auditoria antes de deletar
    deleted_details = {"liters": log_to_delete.liters, "cost": log_to_delete.total_cost}

    await crud.fuel_log.remove_fuel_log(db, db_obj=log_to_delete)
    
    # --- AUDITORIA ---
    try:
        from app.schemas.audit_log_schema import AuditLogCreate
        from app.crud import crud_audit_log
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="DELETE", resource_type="Registro de Abastecimento", resource_id=str(log_id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details=deleted_details
        ))
        await db.commit()
    except Exception:
        pass
    # -----------------

    return Response(status_code=status.HTTP_204_NO_CONTENT)