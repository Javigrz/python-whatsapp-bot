from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar importar la configuración de base de datos
try:
    from src.core.database import init_database, create_tables, health_check, close_database
    DATABASE_AVAILABLE = True
    logger.info("✅ Módulo de base de datos importado correctamente")
except ImportError as e:
    DATABASE_AVAILABLE = False
    logger.warning(f"⚠️ Base de datos no disponible: {e}")

# Intentar importar configuraciones
            # Intentar importar configuraciones
try:
    from src.core.settings import settings
    logger.info("✅ Settings importadas")
except Exception as e:
    logger.warning(f"⚠️ Error importando settings: {e}")
    settings = None

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
    
    # Inicializar base de datos si está disponible
    if DATABASE_AVAILABLE:
        try:
            db_initialized = init_database()
            if db_initialized:
                logger.info("✅ Base de datos inicializada")
                tables_created = create_tables()
                if tables_created:
                    logger.info("✅ Tablas creadas/verificadas")
                else:
                    logger.warning("⚠️ Error creando tablas")
            else:
                logger.warning("⚠️ No se pudo inicializar la base de datos")
        except Exception as e:
            logger.error(f"❌ Error en inicialización de BD: {e}")
    else:
        logger.info("🔄 Ejecutando sin base de datos")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    if DATABASE_AVAILABLE:
        try:
            close_database()
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
        allowed_origins = ["*"]
        if settings and hasattr(settings, 'allowed_origins'):
            allowed_origins = settings.allowed_origins.split(",") if isinstance(settings.allowed_origins, str) else ["*"]
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("✅ CORS configurado")
    except Exception as e:
        logger.error(f"❌ Error configurando CORS: {e}")
    
    # Middleware para inyectar sesión de base de datos (solo si está disponible)
    if DATABASE_AVAILABLE:
        try:
            from src.core.database import get_session
            
            @app.middleware("http")
            async def db_session_middleware(request: Request, call_next):
                try:
                    db_session = get_session()
                    request.state.db = db_session
                    response = await call_next(request)
                    db_session.close()
                    return response
                except Exception as e:
                    logger.error(f"Error en middleware de BD: {e}")
                    # Continuar sin BD si hay error
                    request.state.db = None
                    return await call_next(request)
        except Exception as e:
            logger.error(f"Error configurando middleware de BD: {e}")
    
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
    
    # Health check mejorado
    @app.get("/health")
    async def health_check_endpoint():
        health_status = {
            "status": "healthy", 
            "version": "1.0.0",
            "database": "not_configured",
            "apis": {
                "webhook": HAS_WEBHOOK,
                "ingest": HAS_INGEST,
                "clients": HAS_CLIENTS
            }
        }
        
        # Verificar estado de la base de datos
        if DATABASE_AVAILABLE:
            try:
                db_healthy = health_check()
                health_status["database"] = "connected" if db_healthy else "error"
            except Exception as e:
                health_status["database"] = f"error: {str(e)}"
        
        return health_status
    
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
def get_db_dependency():
    """Dependency para inyectar sesión de base de datos en endpoints"""
    if not DATABASE_AVAILABLE:
        return None
    
    db = get_session()
    try:
        yield db
    finally:
        db.close()