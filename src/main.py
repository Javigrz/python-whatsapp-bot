from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.settings import settings
from src.api import ingest, webhook, clients
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Motor de base de datos
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True
)

# Session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    
    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    await engine.dispose()


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI"""
    app = FastAPI(
        title="Released WhatsApp Bot API",
        version="1.0.0",
        description="API para gestionar bots de WhatsApp Business",
        lifespan=lifespan
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware para inyectar sesión de base de datos
    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        async with async_session() as session:
            request.state.db = session
            response = await call_next(request)
            await session.commit()
            return response
    
    # Incluir routers
    app.include_router(ingest.router, tags=["agents"])
    app.include_router(webhook.router, tags=["webhook"])
    app.include_router(clients.router, tags=["clients"])
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app


# Crear instancia de la aplicación
app = create_app()


# Dependency para obtener la sesión de BD
async def get_session(request: Request) -> AsyncSession:
    return request.state.db 