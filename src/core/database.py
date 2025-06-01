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
        """Obtener la URL de la base de datos con prioridad a host interno de Railway"""
        
        # Verificar si tenemos el host interno de Railway
        postgres_host = os.getenv('POSTGRES_HOST')
        if postgres_host == 'postgres.railway.internal':
            # Usar las variables individuales para construir la URL interna
            db_port = os.getenv('POSTGRES_PORT', '5432')
            db_user = os.getenv('POSTGRES_USER', 'postgres')
            db_password = os.getenv('POSTGRES_PASSWORD')
            db_name = os.getenv('POSTGRES_DB', 'railway')
            
            if db_password:
                database_url = f"postgresql://{db_user}:{db_password}@{postgres_host}:{db_port}/{db_name}"
                logger.info("Usando host interno de Railway PostgreSQL")
                return database_url
        
        # Fallback: usar DATABASE_URL de Railway
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            logger.info("Usando DATABASE_URL de Railway")
            return database_url
        
        # Último fallback: construir desde variables individuales genéricas
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        db_name = os.getenv('POSTGRES_DB', 'whatsapp_bot')
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info("Usando variables individuales de PostgreSQL")
        return database_url
    
    def initialize(self) -> bool:
        """Inicializar la conexión a la base de datos con configuración optimizada para Railway"""
        if self._initialized:
            return True
            
        database_url = self.get_database_url()
        logger.info(f"Conectando a la base de datos...")
        
        railway_env = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_STATIC_URL')
        
        try:
            # Detectar tipo de conexión Railway
            if railway_env:
                postgres_host = os.getenv('POSTGRES_HOST', '')
                
                # Revisamos si estamos usando el nuevo servicio Postgres-Eroj
                if 'postgres-eroj.railway.internal' in postgres_host or 'postgres-eroj.railway.internal' in database_url:
                    # Host interno del nuevo servicio PostgreSQL - configuración óptima
                    logger.info("🔌 Detectado nuevo servicio PostgreSQL-Eroj (interno)")
                    
                    # Preparar conexión específica para Postgres-Eroj
                    connect_args = {
                        "application_name": "whatsapp-bot-eroj",
                        "connect_timeout": 30
                    }
                    
                    self.engine = create_engine(
                        database_url,
                        echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                        pool_pre_ping=True,
                        pool_recycle=300,
                        pool_size=5,
                        max_overflow=10,
                        pool_timeout=30,
                        connect_args=connect_args
                    )
                    
                elif 'shuttle.proxy.rlwy.net' in database_url or 'metro.proxy.rlwy.net' in database_url:
                    # Proxy externo de Railway - configuración especial
                    logger.info("🔌 Detectado nuevo proxy de Railway (shuttle/metro), usando configuración especial")
                    
                    # Primero intentamos con SSL requerido
                    ssl_url = self._add_ssl_mode(database_url, "require")
                    
                    connect_args = {
                        "application_name": "whatsapp-bot-railway-proxy",
                        "connect_timeout": 60,
                        "options": "-c statement_timeout=30s"
                    }
                    
                    self.engine = create_engine(
                        ssl_url,
                        echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                        pool_pre_ping=True,
                        pool_recycle=300,
                        pool_size=3,  # Reducir para proxy
                        max_overflow=5,
                        pool_timeout=60,
                        connect_args=connect_args
                    )
                else:
                    # Railway genérico
                    logger.info("Configuración Railway genérica")
                    connect_args = {"application_name": "whatsapp-bot-railway"}
                    
                    self.engine = create_engine(
                        database_url,
                        echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                        pool_pre_ping=True,
                        pool_recycle=300,
                        connect_args=connect_args
                    )
            else:
                # Configuración local con fallback SSL
                logger.info("Configuración local detectada")
                ssl_modes = ["prefer", "require", "allow", "disable"]
                
                for ssl_mode in ssl_modes:
                    try:
                        test_url = self._add_ssl_mode(database_url, ssl_mode)
                        logger.info(f"Probando conexión local con sslmode={ssl_mode}")
                        
                        connect_args = {"application_name": "whatsapp-bot-local"}
                        
                        self.engine = create_engine(
                            test_url,
                            echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                            pool_pre_ping=True,
                            pool_recycle=300,
                            pool_size=5,
                            max_overflow=10,
                            pool_timeout=30,
                            connect_args=connect_args
                        )
                        
                        # Probar la conexión
                        with self.engine.begin() as conn:
                            result = conn.execute(text("SELECT 1"))
                            result.fetchone()
                        
                        logger.info(f"✅ Conexión local exitosa con sslmode={ssl_mode}")
                        break
                        
                    except Exception as e:
                        logger.warning(f"⚠️  Falló sslmode={ssl_mode}: {str(e)[:80]}")
                        if self.engine:
                            self.engine.dispose()
                            self.engine = None
                        continue
                else:
                    raise Exception("No se pudo establecer conexión local")
            
            # Crear sessionmaker síncrono
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Probar la conexión final
            with self.engine.begin() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self._initialized = True
            logger.info("✅ Conexión a la base de datos establecida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {str(e)}")
            if self.engine:
                self.engine.dispose()
                self.engine = None
            self.SessionLocal = None
            return False
    
    def _add_ssl_mode(self, url: str, ssl_mode: str) -> str:
        """Agregar o modificar el parámetro sslmode en la URL de forma segura"""
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        # Verificar si la URL ya tiene el parámetro sslmode con el mismo valor
        if f"sslmode={ssl_mode}" in url:
            return url
            
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Actualizar o agregar el parámetro sslmode
            query_params['sslmode'] = [ssl_mode]
            
            # Agregar params adicionales para Railway si es necesario
            if ssl_mode == "require" and ("railway.internal" in url or "rlwy.net" in url):
                # Opciones adicionales para certificados
                query_params['sslcert'] = ['']
                query_params['sslkey'] = ['']
                query_params['sslrootcert'] = ['']
            
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            
            return urlunparse(new_parsed)
            
        except Exception as e:
            logger.warning(f"Error al modificar SSL en URL: {e}")
            # Fallback simple si hay error en el parsing
            if '?' in url:
                return f"{url}&sslmode={ssl_mode}"
            else:
                return f"{url}?sslmode={ssl_mode}"
    
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
