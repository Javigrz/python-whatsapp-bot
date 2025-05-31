from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from asyncpg.exceptions import ConnectionDoesNotExistError, PostgresError
from config import *
import logging
import asyncio
from typing import Optional, Dict
import socket
import dns.resolver

logger = logging.getLogger(__name__)

def get_connection_args() -> Dict:
    args = {
        "timeout": CONNECT_TIMEOUT,
        "command_timeout": DB_COMMAND_TIMEOUT,
        "statement_timeout": DB_STATEMENT_TIMEOUT,
        "server_settings": {
            "application_name": "python-whatsapp-bot",
            "client_encoding": "utf8",
            "timezone": "UTC"
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

async def resolve_hostname(hostname: str) -> str:
    if hostname == 'localhost' or socket.inet_aton(hostname):
        return hostname
    
    try:
        answers = dns.resolver.resolve(hostname, 'A')
        return str(answers[0])
    except Exception as e:
        logger.error(f"DNS resolution failed for {hostname}: {str(e)}")
        return hostname

async def init_db() -> Optional[sessionmaker]:
    last_error = None
    
    # Resolver hostname
    resolved_host = await resolve_hostname(DB_HOST)
    connection_url = DATABASE_URL.replace(DB_HOST, resolved_host)
    
    for attempt in range(MAX_RETRIES):
        try:
            engine = create_async_engine(
                connection_url,
                echo=True,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                connect_args=get_connection_args()
            )
            
            # Test connection before creating session
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
                
            async_session = sessionmaker(
                engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            logger.info(f"Conexión establecida exitosamente a {resolved_host}")
            return async_session
                    
        except Exception as e:
            last_error = str(e)
            logger.error(f"Intento {attempt + 1}/{MAX_RETRIES} fallido: {last_error}")
            
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (attempt + 1)  # Backoff exponencial
                logger.info(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
            else:
                logger.critical(f"Fallo de conexión después de {MAX_RETRIES} intentos")
                raise RuntimeError(f"Error de conexión: {last_error}")

    return None
