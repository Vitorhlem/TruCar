from datetime import datetime
import smtplib
import os
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app.core.config import settings
from typing import List, Optional

def send_email(to_emails: List[str], subject: str, message_html: str, attachments: Optional[List[str]] = None):
    """
    Envia um e-mail com suporte opcional a anexos.
    Função SÍNCRONA (Bloqueante) - Deve ser chamada apenas pelo Celery Worker.
    """
    msg = MIMEMultipart()
    msg['From'] = settings.EMAILS_FROM_EMAIL
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(message_html, 'html'))

    if attachments:
        for file_path in attachments:
            try:
                if not os.path.isfile(file_path):
                    print(f"Aviso: Anexo não encontrado em {file_path}")
                    continue

                ctype, encoding = mimetypes.guess_type(file_path)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                
                maintype, subtype = ctype.split('/', 1)

                with open(file_path, 'rb') as f:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                
                filename = os.path.basename(file_path)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(part)
            except Exception as e:
                print(f"Erro ao anexar arquivo {file_path}: {e}")

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"E-mail enviado para: {to_emails} | Anexos: {bool(attachments)}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def get_password_reset_template(user_name: str, token: str) -> str:
    """
    Gera apenas o HTML para o e-mail de recuperação.
    Isso permite passar o HTML texto para o Celery.
    """
    project_name = settings.PROJECT_NAME
    reset_url = f"{settings.FRONTEND_URL}/#/auth/reset-password?token={token}"

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; background-color: #f4f4f7; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .header {{ background-color: #2D3748; color: #ffffff; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; }}
            .content p {{ font-size: 16px; line-height: 1.6; color: #4A5568; }}
            .cta-button {{ display: block; width: 250px; margin: 30px auto; padding: 15px; background-color: #3B82F6; color: #ffffff; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .footer {{ background-color: #1A202C; color: #a0aec0; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><h1>{project_name}</h1></div>
            <div class="content">
                <p>Olá, {user_name},</p>
                <p>Recebemos uma solicitação para redefinir a sua senha.</p>
                <p>Clique no botão abaixo para criar uma nova senha (válido por 60 minutos).</p>
                <a href="{reset_url}" class="cta-button">Redefinir Minha Senha</a>
                <p style="font-size: 12px; text-align: center; color: #718096;">Link alternativo:<br>{reset_url}</p>
            </div>
            <div class="footer">&copy; {datetime.now().year} {project_name}.</div>
        </div>
    </body>
    </html>
    """