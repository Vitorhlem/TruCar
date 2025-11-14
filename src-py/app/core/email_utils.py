from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import List

def send_email(to_emails: List[str], subject: str, message_html: str):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAILS_FROM_EMAIL
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(message_html, 'html'))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"E-mail de notificação enviado com sucesso para: {to_emails}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def send_password_reset_email(to_email: str, user_name: str, token: str):
    """Envia o e-mail de recuperação de senha com o link e o token."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Redefinição de Senha"
    
    # Idealmente, a URL do frontend viria das configurações do ambiente
    reset_url = f"http://localhost:9000/#/auth/reset-password?token={token}"

    message_html = f"""
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
                <p>Recebemos uma solicitação para redefinir a sua senha. Se não foi você quem solicitou, por favor, ignore este e-mail.</p>
                <p>Para criar uma nova senha, clique no botão abaixo. Este link é válido por 60 minutos.</p>
                <a href="{reset_url}" class="cta-button">Redefinir Minha Senha</a>
                <p style="font-size: 12px; text-align: center; color: #718096;">Se o botão não funcionar, copie e cole o seguinte link no seu navegador:<br>{reset_url}</p>
            </div>
            <div class="footer">&copy; {datetime.now().year} {project_name}. Todos os direitos reservados.</div>
        </div>
    </body>
    </html>
    """
    
    send_email(to_emails=[to_email], subject=subject, message_html=message_html)
# --- FIM DA MODIFICAÇÃO ---
