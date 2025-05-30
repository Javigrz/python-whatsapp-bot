from sqlmodel import create_engine, Session
from src.core.settings import settings
from contextlib import contextmanager

# Crear engine síncrono para Celery
sync_engine = create_engine(
    settings.database_url.replace("postgresql+asyncpg", "postgresql"),
    echo=False
)

@contextmanager
def get_sync_session():
    """Crea una sesión síncrona para usar con Celery"""
    with Session(sync_engine) as session:
        yield session 