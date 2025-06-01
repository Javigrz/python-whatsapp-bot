#!/usr/bin/env python3
"""
Script específico para probar conexiones de base de datos en Railway
Resuelve el error "received invalid response to SSL negotiation: H"
"""
import os
import psycopg2
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def modify_database_url(url, ssl_mode, additional_params=None):
    """Modificar la URL de la base de datos con parámetros SSL específicos"""
    parsed = urlparse(url)
    
    # Extraer parámetros existentes
    query_params = parse_qs(parsed.query)
    
    # Agregar/modificar sslmode
    query_params['sslmode'] = [ssl_mode]
    
    # Agregar parámetros adicionales
    if additional_params:
        for key, value in additional_params.items():
            query_params[key] = [value]
    
    # Reconstruir la URL
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)

def test_railway_connection():
    """Probar diferentes configuraciones SSL para Railway"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("❌ No hay DATABASE_URL configurada")
        return False
    
    logger.info(f"🔗 Testing Railway connection...")
    
    # Diferentes configuraciones SSL para probar
    ssl_configs = [
        # Configuración 1: SSL requerido (Railway estándar)
        {
            "ssl_mode": "require",
            "params": None,
            "description": "SSL requerido (Railway estándar)"
        },
        
        # Configuración 2: SSL deshabilitado (para problemas de proxy)
        {
            "ssl_mode": "disable", 
            "params": None,
            "description": "SSL deshabilitado (bypass proxy)"
        },
        
        # Configuración 3: SSL preferido con timeout
        {
            "ssl_mode": "prefer",
            "params": {"connect_timeout": "30"},
            "description": "SSL preferido con timeout"
        },
        
        # Configuración 4: SSL allow (más permisivo)
        {
            "ssl_mode": "allow",
            "params": {"connect_timeout": "30"},
            "description": "SSL allow (permisivo)"
        },
        
        # Configuración 5: Railway con parámetros específicos
        {
            "ssl_mode": "require",
            "params": {
                "connect_timeout": "30",
                "application_name": "railway-whatsapp-bot",
                "options": "-c statement_timeout=30s"
            },
            "description": "Railway optimizado"
        }
    ]
    
    successful_configs = []
    
    for config in ssl_configs:
        try:
            logger.info(f"\n🧪 Probando: {config['description']}")
            
            # Modificar URL con la configuración
            test_url = modify_database_url(
                database_url, 
                config['ssl_mode'], 
                config['params']
            )
            
            logger.info(f"🔗 URL: {test_url[:80]}...")
            
            # Intentar conexión
            conn = psycopg2.connect(test_url)
            cursor = conn.cursor()
            
            # Test básico
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Test de creación de tabla (para verificar permisos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("INSERT INTO test_connection DEFAULT VALUES;")
            cursor.execute("SELECT COUNT(*) FROM test_connection;")
            count = cursor.fetchone()
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ ¡Conexión exitosa!")
            logger.info(f"   PostgreSQL: {version[0][:50]}...")
            logger.info(f"   Registros de prueba: {count[0]}")
            
            successful_configs.append(config)
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "SSL negotiation" in error_msg and "H" in error_msg:
                logger.warning(f"⚠️  Error SSL conocido de Railway: {error_msg[:80]}...")
            else:
                logger.error(f"❌ Error operacional: {error_msg[:80]}...")
        except Exception as e:
            logger.error(f"❌ Error: {str(e)[:80]}...")
    
    if successful_configs:
        logger.info(f"\n✅ Configuraciones exitosas: {len(successful_configs)}")
        for config in successful_configs:
            logger.info(f"   - {config['description']}")
        return True
    else:
        logger.error("\n❌ Ninguna configuración funcionó")
        return False

def test_with_sqlalchemy():
    """Probar con SQLAlchemy usando la configuración exitosa"""
    from sqlalchemy import create_engine, text
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return False
    
    logger.info("\n🔧 Probando con SQLAlchemy...")
    
    # Usar la configuración que más probablemente funcione en Railway
    test_url = modify_database_url(database_url, "require")
    
    try:
        engine = create_engine(
            test_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            connect_args={
                "application_name": "whatsapp-bot-railway",
                "connect_timeout": 30
            }
        )
        
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
        logger.info("✅ SQLAlchemy connection successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLAlchemy error: {str(e)[:80]}...")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando diagnóstico de Railway PostgreSQL")
    
    # Test 1: Conexiones directas con psycopg2
    psycopg2_success = test_railway_connection()
    
    # Test 2: SQLAlchemy
    if psycopg2_success:
        sqlalchemy_success = test_with_sqlalchemy()
    else:
        logger.warning("⚠️  Saltando test de SQLAlchemy (psycopg2 falló)")
        sqlalchemy_success = False
    
    # Resumen
    logger.info("\n📊 RESUMEN:")
    logger.info(f"   psycopg2: {'✅' if psycopg2_success else '❌'}")
    logger.info(f"   SQLAlchemy: {'✅' if sqlalchemy_success else '❌'}")
    
    if psycopg2_success and sqlalchemy_success:
        logger.info("✅ ¡Railway PostgreSQL está funcionando!")
    else:
        logger.error("❌ Problemas de conexión detectados")
