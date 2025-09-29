from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- INÍCIO DA MODIFICAÇÃO: Constantes para o token de reset ---
# Usaremos a REFRESH_TOKEN_SECRET_KEY para isolamento, mas em um projeto maior,
# o ideal seria ter uma chave dedicada (ex: PASSWORD_RESET_SECRET_KEY).
PASSWORD_RESET_SECRET_KEY = settings.REFRESH_TOKEN_SECRET_KEY
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 60  # O token expira em 1 hora
# --- FIM DA MODIFICAÇÃO ---

def create_access_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"} # Adicionado tipo para clareza
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- INÍCIO DA MODIFICAÇÃO: Funções para o token de reset ---
def create_password_reset_token(email: str) -> str:
    """Cria um token de redefinição de senha."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset" # Garante que o token só possa ser usado para isso
    }
    encoded_jwt = jwt.encode(to_encode, PASSWORD_RESET_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verifica o token e retorna o e-mail se for válido."""
    try:
        decoded_token = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Validação extra para garantir que o token é do tipo correto
        if decoded_token.get("type") != "password_reset":
            return None
        return decoded_token.get("sub")
    except JWTError:
        return None
# --- FIM DA MODIFICAÇÃO ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)