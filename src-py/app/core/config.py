from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Set
from pydantic import model_validator, Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    PROJECT_NAME: str = "TruCar"
    API_V1_STR: str = "/api/v1"

    SUPERUSER_EMAILS: Set[str] = {"admin@admin.com", "vitorhugolemes6@gmail.com"}
    
    # Configurações SMTP (Mantidas obrigatórias)
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    
    # O Pydantic lerá a variável do ambiente 'REDIS_URL' se existir
    # Senão, usará o fallback local (Corrigi o IP para local)
    REDIS_URL: str = "redis://127.0.0.1:6379/0" 

    # --- CORREÇÃO DE BANCO DE DADOS ---
    # 1. Tornamos os campos individuais opcionais para que o Render não gere erro 422
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    # 2. Adicionamos o campo que o Render fornece (DATABASE_URL)
    database_url_from_env: Optional[str] = Field(None, alias="DATABASE_URL")
    
    # 3. O resultado final será armazenado neste atributo
    DATABASE_URI: Optional[str] = None
    
    # 4. VALIDADOR: Monta a URI priorizando a DATABASE_URL do Render
    @model_validator(mode='after')
    def assemble_db_uri(self) -> 'Settings':
        # Prioridade 1: Usar a URL completa fornecida pelo Render
        if self.database_url_from_env:
            # Render fornece 'postgres://'. Trocamos para 'postgresql+asyncpg://' (dialeto do SQLAlchemy async).
            uri = self.database_url_from_env.replace("postgres://", "postgresql+asyncpg://", 1)
            self.DATABASE_URI = uri
        
        # Prioridade 2: Usar os campos individuais se todos estiverem presentes (para ambiente local)
        elif self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_SERVER and self.POSTGRES_DB:
             self.DATABASE_URI = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
             )
        
        # 5. Geração de erro claro se faltar configuração em produção
        else:
            raise ValueError("Erro de Configuração: As variáveis do PostgreSQL (DATABASE_URL ou POSTGRES_*) são obrigatórias.")
        
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