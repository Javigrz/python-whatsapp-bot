#!/usr/bin/env python3
"""
Solución robusta para Railway PostgreSQL con proxy externo
"""
import os
import sys
import logging
import psycopg2
from urllib.parse import urlparse

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_railway_proxy_connection():
    """Crear conexión robusta para Railway con proxy externo"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ No hay DATABASE_URL")
        return None
    
    logger.info("🚀 Probando conexión robusta con proxy Railway")
    
    # Configuraciones específicas para el proxy de Railway
    configs_to_try = [
        # Configuración 1: Sin SSL con libpq estándar
        {
            "dsn": database_url + "?sslmode=disable&application_name=railway-whatsapp-bot",
            "description": "Sin SSL con application_name"
        },
        
        # Configuración 2: Sin SSL con timeout extendido
        {
            "dsn": database_url + "?sslmode=disable&connect_timeout=60&application_name=railway-bot",
            "description": "Sin SSL con timeout extendido"
        },
        
        # Configuración 3: Parámetros manuales
        {
            "params": {
                "host": "metro.proxy.rlwy.net",
                "port": 36898,
                "database": "railway",
                "user": "postgres",
                "password": "xTvMbfjLowEBfnnzFNTEdGREoOgcvJEp",
                "sslmode": "disable",
                "connect_timeout": 60,
                "application_name": "railway-whatsapp-bot"
            },
            "description": "Parámetros manuales sin SSL"
        }
    ]
    
    for config in configs_to_try:
        try:
            logger.info(f"\n🧪 Probando: {config['description']}")
            
            if 'dsn' in config:
                conn = psycopg2.connect(config['dsn'])
            else:
                conn = psycopg2.connect(**config['params'])
            
            # Test básico
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Test de creación de tabla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS railway_test (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message TEXT
                );
            """)
            
            # Test de inserción
            cursor.execute(
                "INSERT INTO railway_test (message) VALUES (%s) RETURNING id;",
                ("Railway connection successful",)
            )
            
            test_id = cursor.fetchone()[0]
            conn.commit()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ ¡Conexión exitosa!")
            logger.info(f"   PostgreSQL: {version[0][:50]}...")
            logger.info(f"   Test ID: {test_id}")
            
            return config
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)[:100]}...")
    
    return None

def test_sqlalchemy_with_working_config(working_config):
    """Probar SQLAlchemy con la configuración que funciona"""
    from sqlalchemy import create_engine, text
    
    logger.info("\n🔧 Probando SQLAlchemy con configuración exitosa...")
    
    try:
        database_url = os.getenv('DATABASE_URL')
        
        if working_config.get('dsn'):
            # Usar DSN
            test_url = working_config['dsn']
        else:
            # Usar parámetros para construir URL
            params = working_config['params']
            test_url = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}?sslmode=disable&connect_timeout=60"
        
        engine = create_engine(
            test_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=3,
            max_overflow=5,
            pool_timeout=60,
            connect_args={
                "application_name": "railway-whatsapp-bot-sqlalchemy",
                "connect_timeout": 60
            }
        )
        
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test de creación de tabla con SQLAlchemy
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sqlalchemy_test (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    test_data TEXT
                );
            """))
            
            conn.execute(text(
                "INSERT INTO sqlalchemy_test (test_data) VALUES (:data)"
            ), {"data": "SQLAlchemy Railway test successful"})
        
        engine.dispose()
        
        logger.info("✅ SQLAlchemy también funciona!")
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLAlchemy error: {str(e)[:100]}...")
        return False

if __name__ == "__main__":
    logger.info("🚀 Test robusto Railway PostgreSQL")
    
    # Test 1: Encontrar configuración que funcione
    working_config = create_railway_proxy_connection()
    
    if working_config:
        logger.info(f"\n✅ Configuración exitosa: {working_config['description']}")
        
        # Test 2: SQLAlchemy
        sqlalchemy_ok = test_sqlalchemy_with_working_config(working_config)
        
        if sqlalchemy_ok:
            logger.info("\n🎉 ¡Railway PostgreSQL está completamente funcional!")
            logger.info("Puedes usar esta configuración en tu aplicación.")
        else:
            logger.warning("\n⚠️  psycopg2 funciona pero SQLAlchemy tiene problemas")
    else:
        logger.error("\n❌ No se pudo establecer conexión con Railway PostgreSQL")
