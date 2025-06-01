#!/usr/bin/env python3
"""
Test especial para Railway usando host interno
"""
import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_internal_connection():
    """Probar conexión usando host interno de Railway"""
    
    # Variables de Railway
    internal_configs = [
        # Configuración 1: Host interno con SSL
        {
            "host": "postgres.railway.internal",
            "port": 5432,
            "database": "railway",
            "user": "postgres", 
            "password": "xTvMbfjLowEBfnnzFNTEdGREoOgcvJEp",
            "sslmode": "require",
            "description": "Host interno con SSL"
        },
        
        # Configuración 2: Host interno sin SSL
        {
            "host": "postgres.railway.internal",
            "port": 5432,
            "database": "railway",
            "user": "postgres",
            "password": "xTvMbfjLowEBfnnzFNTEdGREoOgcvJEp", 
            "sslmode": "disable",
            "description": "Host interno sin SSL"
        },
        
        # Configuración 3: URL proxy original con diferentes configuraciones
        {
            "host": "metro.proxy.rlwy.net",
            "port": 36898,
            "database": "railway",
            "user": "postgres",
            "password": "xTvMbfjLowEBfnnzFNTEdGREoOgcvJEp",
            "sslmode": "disable", 
            "description": "Proxy externo sin SSL"
        }
    ]
    
    for config in internal_configs:
        try:
            logger.info(f"\n🧪 Probando: {config['description']}")
            logger.info(f"🔗 Conectando a {config['host']}:{config['port']}")
            
            # Remover 'description' antes de pasar a psycopg2
            connection_params = {k: v for k, v in config.items() if k != 'description'}
            
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()
            
            # Test básico
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Test de permisos
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ ¡Conexión exitosa!")
            logger.info(f"   PostgreSQL: {version[0][:50]}...")
            logger.info(f"   Database: {db_info[0]}, User: {db_info[1]}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)[:100]}...")
    
    return False

def test_railway_env_detection():
    """Verificar detección del entorno Railway"""
    logger.info("\n🔍 Verificando entorno Railway:")
    
    railway_vars = [
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_STATIC_URL', 
        'RAILWAY_SERVICE_NAME',
        'DATABASE_URL'
    ]
    
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"   ✅ {var}: {value[:30]}...")
        else:
            logger.info(f"   ❌ {var}: No configurada")

if __name__ == "__main__":
    logger.info("🚀 Test Railway con host interno")
    
    # Verificar entorno
    test_railway_env_detection()
    
    # Test de conexión
    success = test_internal_connection()
    
    if success:
        logger.info("\n✅ ¡Conexión Railway exitosa!")
    else:
        logger.error("\n❌ Todas las configuraciones fallaron")
