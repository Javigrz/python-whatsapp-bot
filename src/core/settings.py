from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Meta API settings
    access_token: str
    meta_access_token: Optional[str] = None
    app_id: str
    meta_app_id: Optional[str] = None
    app_secret: str
    meta_app_secret: Optional[str] = None
    verify_token: str
    meta_verify_token: Optional[str] = None
    version: str = "v18.0"
    
    # OpenAI settings
    openai_api_key: str
    
    # Database settings
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    database_url: Optional[str] = None
    db_echo: bool = False
    db_pool_size: int = 5
    
    # API settings
    allowed_origins: str = "*"
    port: int = 8082
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    
    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    
    # Celery settings
    celery_broker_url: str
    celery_result_backend: str
    
    # Resend settings
    resend_api_key: Optional[str] = None
    
    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        # Mapear variables de Meta
        self.meta_access_token = self.access_token
        self.meta_app_id = self.app_id
        self.meta_app_secret = self.app_secret
        self.meta_verify_token = self.verify_token
        
        # Configurar URL de base de datos
        self.database_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = 'utf-8'

settings = Settings()