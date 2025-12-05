from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Set, List, Dict, Any
from pydantic import model_validator, Field, AnyHttpUrl, field_validator
import json

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore", case_sensitive=True)

    PROJECT_NAME: str = "TruCar"
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:9000"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SUPERUSER_EMAILS: Set[str] = set()

    @field_validator("SUPERUSER_EMAILS", mode="before")
    @classmethod
    def assemble_superuser_emails(cls, v: Any) -> Any:
        if isinstance(v, str):
            return {i.strip() for i in v.split(",")}
        return v
    
    # Configurações SMTP
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    
    OPENWEATHER_API_KEY: str
    REDIS_URL: str

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

    DEMO_TOTAL_LIMITS: Dict[str, int] = {
        "vehicles": 3,
        "users": 2,
        "parts": 15,
        "clients": 5,
        "implements": 2,
        "vehicle_components": 10,
    }
    
    @field_validator("DEMO_TOTAL_LIMITS", mode="before")
    @classmethod
    def parse_demo_total_limits(cls, v: Any) -> Any:
        if isinstance(v, str):
            return json.loads(v)
        return v

    DEMO_MONTHLY_LIMITS: Dict[str, int] = {
        "reports": 5,
        "fines": 3,
        "documents": 10,
        "freight_orders": 10,
        "maintenance_requests": 5,
        "fuel_logs": 20,
    }

    @field_validator("DEMO_MONTHLY_LIMITS", mode="before")
    @classmethod
    def parse_demo_monthly_limits(cls, v: Any) -> Any:
        if isinstance(v, str):
            return json.loads(v)
        return v

settings = Settings()