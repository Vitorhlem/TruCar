from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Set
from pydantic import model_validator, Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    PROJECT_NAME: str = "TruCar"
    API_V1_STR: str = "/api/v1"

    SUPERUSER_EMAILS: Set[str] = {"admin@admin.com", "vitorhugolemes6@gmail.com"}
    
    # Configurações SMTP
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    OPENWEATHER_API_KEY: str = "chave_temporaria_se_nao_houver_env"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # --- CORREÇÃO: Campos individuais opcionais ---
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    # Campo lido do Render (DATABASE_URL)
    database_url_from_env: Optional[str] = Field(None, alias="DATABASE_URL")
    
    # Resultado final (URI que o SQLAlchemy usa)
    DATABASE_URI: Optional[str] = None
    
    @model_validator(mode='after')
    def assemble_db_uri(self) -> 'Settings':
        uri = None
        
        # Prioridade 1: Usar a URL completa do ambiente (Render)
        if self.database_url_from_env:
            uri = self.database_url_from_env
            
            # CORREÇÃO CRÍTICA: Troca do prefixo síncrono para o assíncrono
            if uri.startswith("postgres://"):
                uri = uri.replace("postgres://", "postgresql+asyncpg://", 1)
            elif uri.startswith("postgresql://") and not uri.startswith("postgresql+asyncpg://"):
                # Garante que substitui o prefixo padrão pelo assíncrono
                uri = uri.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Prioridade 2: Usar os campos individuais para ambiente local (se fornecidos)
        elif self.POSTGRES_USER and self.POSTGRES_SERVER and self.POSTGRES_DB:
             uri = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
             )
        
        if not uri:
             raise ValueError("Configuração do banco de dados inválida. DATABASE_URL ou POSTGRES_* são necessários.")

        self.DATABASE_URI = uri
        return self
    # --- FIM DA CORREÇÃO ---

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    ALGORITHM: str = "HS256"
    FERNET_KEY: str

    DEMO_TOTAL_LIMITS: dict[str, int] = {
        "vehicles": 3,
        "users": 2,
        "parts": 15,
        "clients": 5,
        "implements": 2,
        "vehicle_components": 10,
    }
    DEMO_MONTHLY_LIMITS: dict[str, int] = {
        "reports": 5,
        "fines": 3,
        "documents": 10,
        "freight_orders": 10,
        "maintenance_requests": 5,
        "fuel_logs": 20,
    }

settings = Settings()