# OBS: Trocamos 'shared_task' pela importação da nossa app configurada
from app.core.celery_app import celery_app 
from app.core.email_utils import send_email
from typing import List, Optional
import structlog
import os  # <--- Adicione a importação

logger = structlog.get_logger()

# --- ALTERAÇÃO AQUI ---
# Usamos @celery_app.task em vez de @shared_task
# Isso garante que a tarefa use as configurações de IP fixo (127.0.0.1)
# definidas no arquivo app/core/celery_app.py
@celery_app.task(
    bind=True, 
    max_retries=3, 
    default_retry_delay=60,
    name="send_email_async"
)
def send_email_async(self, to_emails: List[str], subject: str, message_html: str, attachments: Optional[List[str]] = None):
    """
    Tarefa Celery para enviar e-mail de forma assíncrona.
    """
    try:
        logger.info(f"Iniciando envio de e-mail para {to_emails}")
        

        
        send_email(
            to_emails=to_emails,
            subject=subject,
            message_html=message_html,
            attachments=attachments
        )

        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        logger.info("E-mail enviado com sucesso via Celery.")
        return "Sent"
        
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail: {e}. Tentando novamente...")
        raise self.retry(exc=e)