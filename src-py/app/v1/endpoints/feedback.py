
from fastapi import APIRouter, Depends, status, BackgroundTasks, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os
import shutil
import uuid

from app import deps
from app.crud import crud_feedback
from app.schemas.feedback_schema import FeedbackCreate, FeedbackResponse
from app.models.user_model import User
from app.core.config import settings
from app.core.email_utils import send_email
from app.tasks.email_tasks import send_email_async

router = APIRouter()

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def send_feedback(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    # background_tasks: BackgroundTasks, <--- REMOVIDO
    type: str = Form(...),
    message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Envia um novo feedback, salva anexo se houver e notifica admins por e-mail.
    """
    
    feedback_in = FeedbackCreate(type=type, message=message)

    # 1. Salva no Banco de Dados
    feedback = await crud_feedback.create_feedback(
        db=db,
        feedback_in=feedback_in,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )

    # 2. Processamento do Arquivo (Se houver)
    attachment_path = None
    file_url_info = ""
    
    if file:
        try:
            # Define diretório de upload (mesmo usado no main.py)
            UPLOAD_DIR = "static/uploads"
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # Gera nome único para evitar colisão
            file_ext = os.path.splitext(file.filename)[1]
            # Ex: feedback_123_uuid8chars.png
            unique_filename = f"feedback_{feedback.id}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # Salva o arquivo no disco
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            attachment_path = file_path
            file_url_info = f"<p><strong>Anexo:</strong> O arquivo <em>{file.filename}</em> foi anexado a este e-mail.</p>"
            
        except Exception as e:
            print(f"Erro ao salvar anexo de feedback: {e}")
            file_url_info = f"<p><strong>Erro:</strong> O usuário tentou enviar {file.filename}, mas houve falha ao salvar.</p>"

    # 3. Prepara o E-mail
    destinatarios = list(settings.SUPERUSER_EMAILS)
    
    if destinatarios:
        subject = f"[TruCar Feedback] Novo {feedback.type}: #{feedback.id}"
        
        message_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #1976D2; color: white; padding: 15px; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .label {{ font-weight: bold; color: #555; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Novo Feedback Recebido</h2>
            </div>
            <div class="content">
                <p><span class="label">Tipo:</span> {feedback.type}</p>
                <p><span class="label">Usuário:</span> {current_user.full_name} ({current_user.email})</p>
                <p><span class="label">Organização ID:</span> {current_user.organization_id}</p>
                <hr>
                <p><span class="label">Mensagem:</span></p>
                <p style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #1976D2;">
                    {feedback.message}
                </p>
                {file_url_info}
            </div>
        </body>
        </html>
        """

        # Prepara a lista de anexos (se houver)
        attachments_list = [attachment_path] if attachment_path else None

        # 4. Envia em Segundo Plano
        send_email_async.delay(
            to_emails=destinatarios,
            subject=subject,
            message_html=message_html,
            attachments=attachments_list
        )

    return feedback
