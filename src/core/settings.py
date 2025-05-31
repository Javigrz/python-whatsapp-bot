from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Meta API settings
    access_token: Optional[str] = None
    meta_access_token: Optional[str] = None
    app_id: Optional[str] = None
    meta_app_id: Optional[str] = None
    app_secret: Optional[str] = None
    meta_app_secret: Optional[str] = None
    verify_token: str = "default_verify_token"
    meta_verify_token: Optional[str] = None
    version: str = "v18.0"
    phone_number_id: Optional[str] = None
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_assistant_id: Optional[str] = None
    
    # Database settings (Railway proporciona DATABASE_URL)
    database_url: Optional[str] = None
    postgres_user: Optional[str] = "postgres"
    postgres_password: Optional[str] = "postgres"
    postgres_db: Optional[str] = "whatsapp_bot"
    postgres_host: Optional[str] = "localhost"
    postgres_port: Optional[str] = "5432"
    db_echo: bool = False
    db_pool_size: int = 5
    
    # API settings
    allowed_origins: str = "*"
    port: int = 8000  # Railway usa PORT env var
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    
    # Redis settings (opcionales para Railway)
    redis_host: Optional[str] = "localhost"
    redis_port: int = 6379
    redis_url: Optional[str] = None
    
    # Celery settings (opcionales)
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # Resend settings
    resend_api_key: Optional[str] = None
    
    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        
        # Mapear variables de Meta si están disponibles
        if self.access_token:
            self.meta_access_token = self.access_token
        if self.app_id:
            self.meta_app_id = self.app_id
        if self.app_secret:
            self.meta_app_secret = self.app_secret
        if self.verify_token:
            self.meta_verify_token = self.verify_token
        
        # Railway proporciona DATABASE_URL automáticamente
        if not self.database_url and os.getenv('DATABASE_URL'):
            self.database_url = os.getenv('DATABASE_URL')
        
        # Si no hay DATABASE_URL, construir una
        if not self.database_url and all([self.postgres_user, self.postgres_password, 
                                         self.postgres_host, self.postgres_port, self.postgres_db]):
            self.database_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
        # Configurar Redis URL si no está disponible
        if not self.redis_url and self.redis_host:
            self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/0"
        
        # Configurar Celery si Redis está disponible
        if not self.celery_broker_url and self.redis_url:
            self.celery_broker_url = self.redis_url
            self.celery_result_backend = self.redis_url

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = 'utf-8'
        extra = "ignore"  # Ignorar variables extra

settings = Settings()