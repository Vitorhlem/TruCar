from cryptography.fernet import Fernet
from app.core.config import settings

# Garante que a chave de criptografia tenha o tamanho correto (32 bytes)
# É crucial que a FERNET_KEY no seu .env seja uma chave válida de 32 bytes.
# Você pode gerar uma com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
try:
    key = settings.FERNET_KEY.encode()
    fernet = Fernet(key)
except Exception as e:
    raise ValueError("FERNET_KEY inválida ou não definida nas configurações. Por favor, gere uma chave válida de 32 bytes.") from e

def encrypt_data(data: str) -> bytes:
    """Criptografa uma string."""
    if not data:
        return b''
    return fernet.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes) -> str:
    """Descriptografa bytes de volta para uma string."""
    if not encrypted_data:
        return ''
    return fernet.decrypt(encrypted_data).decode()
