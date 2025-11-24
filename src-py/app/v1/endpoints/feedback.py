from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import deps
from app.crud import crud_feedback
from app.schemas.feedback_schema import FeedbackCreate, FeedbackResponse
from app.models.user_model import User
from app.core.config import settings
from app.core.email_utils import send_email

router = APIRouter()

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def send_feedback(
    *,
    feedback_in: FeedbackCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks # Adicionado para não travar a resposta
):
    """
    Envia um novo feedback e notifica os administradores por e-mail.
    """
    # 1. Salva no Banco de Dados
    feedback = await crud_feedback.create_feedback(
        db=db,
        feedback_in=feedback_in,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )

    # 2. Prepara o E-mail
    # O destino são os emails definidos em config.py
    destinatarios = list(settings.SUPERUSER_EMAILS)
    
    if destinatarios:
        subject = f"[TruCar Feedback] Novo {feedback.type}: #{feedback.id}"
        
        # Formato HTML do e-mail
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
            </div>
        </body>
        </html>
        """

        # 3. Envia em Segundo Plano (Background Task)
        # Usamos background_tasks para que o usuário não espere o e-mail ser enviado
        background_tasks.add_task(
            send_email,
            to_emails=destinatarios,
            subject=subject,
            message_html=message_html
        )

    return feedback