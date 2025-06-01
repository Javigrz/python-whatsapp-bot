"""
Módulo de base de datos para WhatsApp Bot
Configuración optimizada para Railway con PostgreSQL (versión síncrona)
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from sqlmodel import SQLModel
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def get_database_url(self) -> str:
        """Obtener la URL de la base de datos desde las variables de entorno"""
        # Priorizar DATABASE_URL de Railway
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Para Railway, asegurar que usamos psycopg2 (síncrono)
            if database_url.startswith('postgresql://'):
                # Agregar configuración SSL para Railway
                if '?' not in database_url:
                    database_url = database_url + "?sslmode=require"
                elif 'sslmode' not in database_url:
                    database_url = database_url + "&sslmode=require"
                
            logger.info("Usando DATABASE_URL de Railway")
            return database_url
        
        # Fallback: construir desde variables individuales
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        db_name = os.getenv('POSTGRES_DB', 'whatsapp_bot')
        
        # Usar postgresql:// (psycopg2) en lugar de postgresql+asyncpg://
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info("Usando variables individuales de PostgreSQL")
        return database_url
    
    def initialize(self) -> bool:
        """Inicializar la conexión a la base de datos"""
        if self._initialized:
            return True
            
        try:
            database_url = self.get_database_url()
            logger.info(f"Conectando a la base de datos...")
            
            # Configuración del engine para Railway (síncrono)
            connect_args = {}
            
            # Para Railway en producción
            if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
                connect_args = {
                    "options": "-c timezone=UTC",
                    "application_name": "whatsapp-bot-railway"
                }
            
            self.engine = create_engine(
                database_url,
                echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
                max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
                connect_args=connect_args
            )
            
            # Crear sessionmaker síncrono
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Probar la conexión
            with self.engine.begin() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self._initialized = True
            logger.info("✅ Conexión a la base de datos establecida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {str(e)}")
            return False
    
    def create_tables(self) -> bool:
        """Crear todas las tablas definidas en los modelos"""
        if not self._initialized:
            self.initialize()
        
        if not self.engine:
            logger.error("Engine no inicializado")
            return False
            
        try:
            # Importar modelos para que SQLModel los registre
            from .models import Agent, Client, Thread
            
            # Crear todas las tablas
            SQLModel.metadata.create_all(bind=self.engine)
            
            logger.info("✅ Tablas creadas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al crear las tablas: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """Verificar el estado de la conexión"""
        if not self._initialized or not self.SessionLocal:
            return False
            
        try:
            with self.SessionLocal() as session:
                result = session.execute(text("SELECT 1"))
                result.fetchone()
            return True
        except Exception as e:
            logger.error(f"Health check falló: {str(e)}")
            return False
    
    def get_session(self) -> Session:
        """Obtener una sesión de base de datos"""
        if not self._initialized:
            self.initialize()
        
        if not self.SessionLocal:
            raise RuntimeError("Base de datos no inicializada")
            
        return self.SessionLocal()
    
    def close(self):
        """Cerrar la conexión a la base de datos"""
        if self.engine:
            self.engine.dispose()
            self._initialized = False
            logger.info("Conexión a la base de datos cerrada")

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones de conveniencia
def init_database() -> bool:
    """Inicializar la base de datos"""
    return db_manager.initialize()

def create_tables() -> bool:
    """Crear las tablas"""
    return db_manager.create_tables()

def get_session() -> Session:
    """Obtener una sesión de base de datos"""
    return db_manager.get_session()

def health_check() -> bool:
    """Verificar el estado de la base de datos"""
    return db_manager.health_check()

def close_database():
    """Cerrar la conexión a la base de datos"""
    db_manager.close()
