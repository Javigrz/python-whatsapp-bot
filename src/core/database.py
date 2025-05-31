"""
Módulo de base de datos para WhatsApp Bot
Configuración optimizada para Railway con PostgreSQL
"""

import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session = None
        self._initialized = False
    
    def get_database_url(self) -> str:
        """Obtener la URL de la base de datos desde las variables de entorno"""
        # Priorizar DATABASE_URL de Railway
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Railway proporciona DATABASE_URL con postgresql://, 
            # pero necesitamos postgresql+asyncpg:// para SQLAlchemy async
            if database_url.startswith('postgresql://'):
                database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
            logger.info("Usando DATABASE_URL de Railway")
            return database_url
        
        # Fallback: construir desde variables individuales
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        db_name = os.getenv('POSTGRES_DB', 'whatsapp_bot')
        
        database_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info("Usando variables individuales de PostgreSQL")
        return database_url
    
    async def initialize(self) -> bool:
        """Inicializar la conexión a la base de datos"""
        if self._initialized:
            return True
            
        try:
            database_url = self.get_database_url()
            logger.info(f"Conectando a la base de datos...")
            
            # Configuración del engine para Railway
            connect_args = {}
            if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
                connect_args = {
                    "server_settings": {
                        "application_name": "whatsapp-bot-railway"
                    }
                }
            
            self.engine = create_async_engine(
                database_url,
                echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
                max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
                connect_args=connect_args
            )
            
            # Crear sessionmaker
            self.async_session = sessionmaker(
                self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            # Probar la conexión
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self._initialized = True
            logger.info("✅ Conexión a la base de datos establecida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {str(e)}")
            return False
    
    async def create_tables(self) -> bool:
        """Crear todas las tablas definidas en los modelos"""
        if not self._initialized:
            await self.initialize()
        
        if not self.engine:
            logger.error("Engine no inicializado")
            return False
            
        try:
            # Importar modelos para que SQLModel los registre
            from .models import Agent, Client, Thread
            
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            
            logger.info("✅ Tablas creadas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al crear las tablas: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Verificar el estado de la conexión"""
        if not self._initialized or not self.async_session:
            return False
            
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
            return True
        except Exception as e:
            logger.error(f"Health check falló: {str(e)}")
            return False
    
    async def get_session(self) -> AsyncSession:
        """Obtener una sesión de base de datos"""
        if not self._initialized:
            await self.initialize()
        
        if not self.async_session:
            raise RuntimeError("Base de datos no inicializada")
            
        return self.async_session()
    
    async def close(self):
        """Cerrar la conexión a la base de datos"""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Conexión a la base de datos cerrada")

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones de conveniencia
async def init_database() -> bool:
    """Inicializar la base de datos"""
    return await db_manager.initialize()

async def create_tables() -> bool:
    """Crear las tablas"""
    return await db_manager.create_tables()

async def get_session() -> AsyncSession:
    """Obtener una sesión de base de datos"""
    return await db_manager.get_session()

async def health_check() -> bool:
    """Verificar el estado de la base de datos"""
    return await db_manager.health_check()

async def close_database():
    """Cerrar la conexión a la base de datos"""
    await db_manager.close()
