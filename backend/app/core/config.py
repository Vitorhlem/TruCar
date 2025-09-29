from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Set

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    PROJECT_NAME: str = "TruCar"
    API_V1_STR: str = "/api/v1"

    SUPERUSER_EMAILS: Set[str] = {"admin@admin.com"}

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str

    # Estas variáveis agora são opcionais
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URI: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        # SÓ MONTA A URI SE ELA NÃO FOR FORNECIDA DIRETAMENTE
        if self.DATABASE_URI is None and self.POSTGRES_USER and self.POSTGRES_SERVER:
            self.DATABASE_URI = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    ALGORITHM: str = "HS256"

    FERNET_KEY: str

settings = Settings()