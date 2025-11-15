from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
import uuid
import shutil
from app.core.email_utils import send_email

from app import crud, deps
from app.models.user_model import User, UserRole
from app.schemas.maintenance_schema import (
    MaintenanceRequestPublic, MaintenanceRequestCreate, MaintenanceRequestUpdate,
    MaintenanceCommentPublic, MaintenanceCommentCreate,
    ReplaceComponentPayload, ReplaceComponentResponse  # <-- 1. IMPORTAR NOVOS SCHEMAS
)
from app.models.notification_model import NotificationType

router = APIRouter()



def send_new_request_email_background(manager_emails: List[str], request: MaintenanceRequestPublic):
    """
    Função síncrona que será executada em segundo plano para enviar os e-mails.
    """
    if not manager_emails:
        print("Nenhum gestor encontrado para enviar notificação por e-mail.")
        return

    subject = f"Novo Chamado de Manutenção Aberto - TruCar #{request.id}"
    
    # Template HTML para o e-mail
    message_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; background-color: #f4f4f7; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .header {{ background-color: #2D3748; color: #ffffff; padding: 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .content p {{ font-size: 16px; line-height: 1.6; color: #4A5568; }}
            .details-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .details-table th, .details-table td {{ padding: 12px; border: 1px solid #e2e8f0; text-align: left; }}
            .details-table th {{ background-color: #edf2f7; width: 30%; }}
            .cta-button {{ display: block; width: 200px; margin: 30px auto; padding: 15px; background-color: #3B82F6; color: #ffffff; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .footer {{ background-color: #1A202C; color: #a0aec0; padding: 20px; text-align: center; font-size: 12px; }}
            .footer a {{ color: #3B82F6; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TruCar - Novo Chamado</h1>
            </div>
            <div class="content">
                <p>Olá,</p>
                <p>Um novo chamado de manutenção foi aberto e precisa da sua atenção.</p>
                <table class="details-table">
                    <tr><th>Chamado Nº</th><td>{request.id}</td></tr>
                    <tr><th>Solicitante</th><td>{request.reporter.full_name}</td></tr>
                    <tr><th>Veículo</th><td>{request.vehicle.brand} {request.vehicle.model} ({request.vehicle.license_plate})</td></tr>
                    <tr><th>Categoria</th><td>{request.category.value}</td></tr>
                </table>
                <p><b>Problema Reportado:</b></p>
                <p><i>{request.problem_description}</i></p>
                <a href="http://localhost:9000/#/maintenance" class="cta-button">Ver Chamado no Sistema</a>
            </div>
            <div class="footer">
                &copy; {datetime.now().year} Vitor H. Lemes - <a href="https://vytruve.org/">vytruve.org</a>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(to_emails=manager_emails, subject=subject, message_html=message_html)

@router.post("/", response_model=MaintenanceRequestPublic, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(deps.check_demo_limit("maintenances"))])
async def create_maintenance_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    request_in: MaintenanceRequestCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        request = await crud.maintenance.create_request(
            db=db, request_in=request_in, reporter_id=current_user.id, organization_id=current_user.organization_id
        )
        
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="maintenances")
        
        message = f"Nova solicitação de manutenção para {request.vehicle.brand} {request.vehicle.model} aberta por {current_user.full_name}."
        background_tasks.add_task(
            crud.notification.create_notification,
            db=db, message=message, notification_type=NotificationType.MAINTENANCE_REQUEST_NEW,
            organization_id=current_user.organization_id, send_to_managers=True,
            related_entity_type="maintenance_request", related_entity_id=request.id,
            related_vehicle_id=request.vehicle_id
        )
        return request
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_id: int,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Deleta uma solicitação de manutenção (apenas para gestores)."""
    request_to_delete = await crud.maintenance.get_request(
        db=db, request_id=request_id, organization_id=current_user.organization_id
    )
    if not request_to_delete:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
        
    await crud.maintenance.delete_request(db=db, request_to_delete=request_to_delete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/", response_model=List[MaintenanceRequestPublic])
async def read_maintenance_requests(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    """Retorna as solicitações de manutenção. Gestores veem tudo, motoristas veem apenas o que reportaram."""
    requests = await crud.maintenance.get_all_requests(
        db=db, organization_id=current_user.organization_id, search=search, skip=skip, limit=limit
    )
    if current_user.role == UserRole.DRIVER:
        return [req for req in requests if req.reported_by_id == current_user.id]
    return requests

@router.put("/{request_id}/status", response_model=MaintenanceRequestPublic)
async def update_request_status(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    request_id: int,
    update_data: MaintenanceRequestUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    db_obj = await crud.maintenance.get_request(db, request_id=request_id, organization_id=current_user.organization_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
        
    updated_request = await crud.maintenance.update_request_status(
        db=db, db_obj=db_obj, update_data=update_data, manager_id=current_user.id
    )
    
    message = f"O status da sua solicitação de manutenção (#{updated_request.id}) foi atualizado para: {updated_request.status.value}."
    background_tasks.add_task(
        crud.notification.create_notification,
        db=db,
        message=message,
        notification_type=NotificationType.MAINTENANCE_REQUEST_STATUS_UPDATE,
        user_id=updated_request.reported_by_id,
        organization_id=current_user.organization_id,
        related_entity_type="maintenance_request",
        related_entity_id=updated_request.id
    )
        
    return updated_request



@router.get("/{request_id}/comments", response_model=List[MaintenanceCommentPublic])
async def read_comments_for_request(
    request_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retorna os comentários de uma solicitação de manutenção."""
    comments = await crud.maintenance_comment.get_comments_for_request(
        db=db, request_id=request_id, organization_id=current_user.organization_id
    )
    # A função CRUD já valida o acesso, então aqui só retornamos
    return comments


@router.post("/{request_id}/comments", response_model=MaintenanceCommentPublic, status_code=status.HTTP_201_CREATED)
async def create_comment_for_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    request_id: int,
    comment_in: MaintenanceCommentCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        comment = await crud.maintenance.create_comment(
            db, comment_in=comment_in, request_id=request_id, user_id=current_user.id, organization_id=current_user.organization_id
        )
        
        request_obj = await crud.maintenance.get_request(db, request_id=request_id, organization_id=current_user.organization_id)
        if request_obj:
            message = f"Novo comentário de {current_user.full_name} na solicitação de manutenção #{request_id}."
            # Se quem comentou foi um motorista, notifica os gestores
            if current_user.role == UserRole.DRIVER:
                background_tasks.add_task(
                    crud.notification.create_notification, db=db, message=message,
                    notification_type=NotificationType.MAINTENANCE_REQUEST_NEW_COMMENT,
                    organization_id=current_user.organization_id, send_to_managers=True,
                    related_entity_type="maintenance_request", related_entity_id=request_id
                )
            # Se quem comentou foi um gestor, notifica o motorista que criou a solicitação
            else:
                background_tasks.add_task(
                    crud.notification.create_notification, db=db, message=message,
                    notification_type=NotificationType.MAINTENANCE_REQUEST_NEW_COMMENT,
                    organization_id=current_user.organization_id, user_id=request_obj.reported_by_id,
                    related_entity_type="maintenance_request", related_entity_id=request_id
                )

        return comment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upload-file", response_model=dict)
async def upload_attachment_file(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Recebe um arquivo, salva-o localmente e retorna a URL de acesso."""
    file_extension = file.filename.split(".")[-1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = f"static/uploads/{unique_filename}"
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    return {"file_url": f"/{file_location}"}

@router.post("/{request_id}/replace-component", response_model=ReplaceComponentResponse)
async def replace_maintenance_component(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    request_id: int,
    payload: ReplaceComponentPayload,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Endpoint atômico para substituir um componente no contexto de um chamado.
    """
    try:
        response = await crud.maintenance.replace_component_atomic(
            db=db,
            request_id=request_id,
            payload=payload,
            user=current_user
        )
        
        # Se tudo deu certo nas funções CRUD (que usam flush), commitamos a transação.
        await db.commit()
        
        # Recarregar o comentário com todas as relações (usuário)
        await db.refresh(response.new_comment, ["user"])
        await db.refresh(response.new_comment.user, ["organization"])
        
        # Notificar o motorista (em background)
        request_obj = await crud.maintenance.get_request(db, request_id=request_id, organization_id=current_user.organization_id)
        if request_obj:
             background_tasks.add_task(
                crud.notification.create_notification, db=db, message=response.new_comment.comment_text,
                notification_type=NotificationType.MAINTENANCE_REQUEST_NEW_COMMENT,
                organization_id=current_user.organization_id, user_id=request_obj.reported_by_id,
                related_entity_type="maintenance_request", related_entity_id=request_id
            )

        return response

    except ValueError as e:
        # Se qualquer passo da lógica de negócio falhar, damos rollback
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Erro genérico
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar a substituição: {e}"
        )