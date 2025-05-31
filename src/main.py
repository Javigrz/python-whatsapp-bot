from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar variables globales
engine = None
async_session = None

# Intentar importar y configurar la base de datos
try:
    from sqlmodel import SQLModel
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from src.core.settings import settings
    
    # Solo configurar BD si tenemos DATABASE_URL
    if settings.database_url:
        logger.info(f"Configurando base de datos: {settings.database_url[:50]}...")
        database_url = str(settings.database_url)
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        engine = create_async_engine(
            database_url,
            echo=settings.db_echo,
            future=True,
            pool_size=settings.db_pool_size,
            max_overflow=64,
        )
        
        async_session = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        logger.info("✅ Base de datos configurada")
    else:
        logger.warning("⚠️ DATABASE_URL no configurada, funcionando sin BD")
        
except Exception as e:
    logger.error(f"❌ Error configurando base de datos: {e}")
    logger.info("Continuando sin base de datos...")

# Intentar importar las APIs
try:
    from src.api import webhook
    logger.info("✅ API webhook importada")
    HAS_WEBHOOK = True
except Exception as e:
    logger.error(f"❌ Error importando webhook: {e}")
    HAS_WEBHOOK = False

try:
    from src.api import ingest
    logger.info("✅ API ingest importada")
    HAS_INGEST = True
except Exception as e:
    logger.error(f"❌ Error importando ingest: {e}")
    HAS_INGEST = False

try:
    from src.api import clients
    logger.info("✅ API clients importada")
    HAS_CLIENTS = True
except Exception as e:
    logger.error(f"❌ Error importando clients: {e}")
    HAS_CLIENTS = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    
    # Crear tablas solo si tenemos BD configurada
    if engine and 'SQLModel' in globals():
        try:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("✅ Tablas de base de datos creadas")
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    if engine:
        try:
            await engine.dispose()
            logger.info("✅ Conexiones de BD cerradas")
        except Exception as e:
            logger.error(f"❌ Error cerrando BD: {e}")


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI"""
    app = FastAPI(
        title="Released WhatsApp Bot API",
        version="1.0.0",
        description="API para gestionar bots de WhatsApp Business",
        lifespan=lifespan,
        root_path=""
    )
    
    # Configurar CORS
    try:
        allowed_origins = getattr(settings, 'allowed_origins', "*")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins.split(",") if isinstance(allowed_origins, str) else ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("✅ CORS configurado")
    except Exception as e:
        logger.error(f"❌ Error configurando CORS: {e}")
    
    # Middleware para inyectar sesión de base de datos (solo si está disponible)
    if async_session:
        @app.middleware("http")
        async def db_session_middleware(request: Request, call_next):
            try:
                async with async_session() as session:
                    request.state.db = session
                    response = await call_next(request)
                    await session.commit()
                    return response
            except Exception as e:
                logger.error(f"Error en middleware de BD: {e}")
                request.state.db = None
                return await call_next(request)
        logger.info("✅ Middleware de BD configurado")
    
    # Incluir routers solo si están disponibles
    if HAS_INGEST:
        app.include_router(ingest.router, tags=["agents"])
        logger.info("✅ Router ingest incluido")
    
    if HAS_WEBHOOK:
        app.include_router(webhook.router, tags=["webhook"])
        logger.info("✅ Router webhook incluido")
    
    if HAS_CLIENTS:
        app.include_router(clients.router, tags=["clients"])
        logger.info("✅ Router clients incluido")
    
    # Health check básico
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy", 
            "version": "1.0.0",
            "database": "connected" if engine else "not_configured",
            "apis": {
                "webhook": HAS_WEBHOOK,
                "ingest": HAS_INGEST,
                "clients": HAS_CLIENTS
            }
        }
    
    # Endpoint de información básica
    @app.get("/")
    async def root():
        return {
            "message": "Released WhatsApp Bot API",
            "version": "1.0.0",
            "status": "running"
        }
    
    logger.info("✅ Aplicación FastAPI creada")
    return app


# Crear instancia de la aplicación
app = create_app()

# Dependency para obtener la sesión de BD (solo si está disponible)
async def get_db():
    if not async_session:
        yield None
        return
    
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()