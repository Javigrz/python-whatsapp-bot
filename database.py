from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from asyncpg.exceptions import ConnectionDoesNotExistError, PostgresError
from config import *
import logging
import asyncio
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def get_connection_args() -> Dict:
    args = {
        "timeout": CONNECT_TIMEOUT,
        "command_timeout": CONNECT_TIMEOUT,
        "server_settings": {
            "application_name": "python-whatsapp-bot"
        }
    }
    
    if SSL_MODE:
        args["ssl"] = SSL_MODE
        if SSL_CERT_PATH:
            args["ssl_cert"] = SSL_CERT_PATH
            
    return args

async def health_check(conn) -> bool:
    try:
        async with conn.acquire() as connection:
            await connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Health check falló: {str(e)}")
        return False

async def init_db() -> Optional[sessionmaker]:
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            engine = create_async_engine(
                DATABASE_URL,
                echo=True,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                connect_args=get_connection_args()
            )
            
            async_session = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            # Verificar conexión
            async with engine.connect() as conn:
                if await health_check(conn):
                    logger.info("Conexión a la base de datos establecida exitosamente")
                    return async_session
                    
        except ConnectionDoesNotExistError as e:
            last_error = f"Error de conexión: {str(e)}"
        except PostgresError as e:
            last_error = f"Error de PostgreSQL: {str(e)}"
        except Exception as e:
            last_error = f"Error inesperado: {str(e)}"
            
        logger.error(f"Intento {attempt + 1}/{MAX_RETRIES} fallido: {last_error}")
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
        else:
            logger.critical(f"No se pudo establecer conexión con la base de datos después de {MAX_RETRIES} intentos")
            raise RuntimeError(f"Error de conexión: {last_error}")

    return None
