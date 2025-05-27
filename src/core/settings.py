from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # General
    app_env: str = "prod"
    port: int = 8080
    allowed_origins: str = "*"
    
    # Meta - Mapeamos a los nombres que ya tienes
    meta_access_token: str = ""
    access_token: Optional[str] = None  # Tu variable actual
    meta_app_secret: str = ""
    app_secret: Optional[str] = None  # Tu variable actual
    phone_number_id: Optional[str] = None  # Ahora es opcional, se obtiene de la BD
    
    # OpenAI
    openai_api_key: str
    openai_assistant_id: Optional[str] = None  # Para usar el assistant existente
    
    # DB
    postgres_user: str = "released"
    postgres_password: str = "released"
    postgres_db: str = "released"
    database_url: str = "postgresql+asyncpg://released:released@db:5432/released"
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    # WhatsApp
    verify_token: str = "13"
    app_id: Optional[str] = None
    version: str = "v18.0"

    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Mapear las variables antiguas a las nuevas si existen
        if self.access_token and not self.meta_access_token:
            self.meta_access_token = self.access_token
        if self.app_secret and not self.meta_app_secret:
            self.meta_app_secret = self.app_secret


settings = Settings() 