#!/usr/bin/env python3
"""
Test alternativo para Railway con configuración específica de psycopg2
"""
import os
import psycopg2
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_psycopg2():
    """Probar conexión directa con psycopg2 usando configuración manual"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ No hay DATABASE_URL")
        return False
    
    logger.info("🚀 Probando conexión directa con psycopg2")
    
    # Parsear la URL manualmente
    parsed = urlparse(database_url)
    
    # Configuraciones específicas para Railway
    connection_configs = [
        # Configuración 1: Sin SSL, solo TCP
        {
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path[1:],
            "user": parsed.username,
            "password": parsed.password,
            "sslmode": "disable",
            "connect_timeout": 30
        },
        
        # Configuración 2: SSL allow (más permisivo)
        {
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path[1:],
            "user": parsed.username,
            "password": parsed.password,
            "sslmode": "allow",
            "connect_timeout": 30
        },
        
        # Configuración 3: URL directa con parámetros
        {
            "dsn": f"{database_url}?sslmode=disable&connect_timeout=30"
        },
        
        # Configuración 4: URL con diferentes SSL modes
        {
            "dsn": f"{database_url}?sslmode=prefer&connect_timeout=30"
        }
    ]
    
    for i, config in enumerate(connection_configs, 1):
        try:
            logger.info(f"\n🧪 Configuración {i}:")
            
            if 'dsn' in config:
                logger.info(f"   DSN: {config['dsn'][:60]}...")
                conn = psycopg2.connect(config['dsn'])
            else:
                logger.info(f"   Host: {config['host']}:{config['port']}")
                logger.info(f"   SSL: {config.get('sslmode', 'default')}")
                conn = psycopg2.connect(**config)
            
            # Test de conexión
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            
            # Test de escritura
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_railway_connection (
                    id SERIAL PRIMARY KEY,
                    test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message TEXT
                );
            """)
            
            cursor.execute(
                "INSERT INTO test_railway_connection (message) VALUES (%s) RETURNING id;",
                ("Railway connection test successful",)
            )
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ ¡Conexión exitosa!")
            logger.info(f"   PostgreSQL: {version[0][:50]}...")
            logger.info(f"   Database: {db_info[0]}, User: {db_info[1]}")
            logger.info(f"   Test record ID: {new_id}")
            
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "SSL negotiation" in error_msg and "H" in error_msg:
                logger.warning(f"⚠️  Error SSL conocido: {error_msg[:80]}...")
            elif "timeout" in error_msg.lower():
                logger.warning(f"⚠️  Timeout: {error_msg[:80]}...")
            else:
                logger.error(f"❌ Error operacional: {error_msg[:80]}...")
                
        except Exception as e:
            logger.error(f"❌ Error: {str(e)[:80]}...")
    
    return False

def test_with_raw_socket():
    """Probar conectividad básica con socket"""
    import socket
    
    database_url = os.getenv('DATABASE_URL')
    parsed = urlparse(database_url)
    
    logger.info(f"\n🔌 Probando conectividad de socket a {parsed.hostname}:{parsed.port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((parsed.hostname, parsed.port))
        sock.close()
        
        if result == 0:
            logger.info("✅ Socket conecta correctamente")
            return True
        else:
            logger.error(f"❌ Socket falló con código: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error de socket: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Test avanzado Railway PostgreSQL")
    
    # Test 1: Conectividad básica
    socket_ok = test_with_raw_socket()
    
    # Test 2: Conexión PostgreSQL
    if socket_ok:
        psycopg2_ok = test_direct_psycopg2()
    else:
        logger.warning("⚠️  Saltando test psycopg2 (socket falló)")
        psycopg2_ok = False
    
    # Resumen
    logger.info(f"\n📊 RESUMEN:")
    logger.info(f"   Socket: {'✅' if socket_ok else '❌'}")
    logger.info(f"   PostgreSQL: {'✅' if psycopg2_ok else '❌'}")
    
    if psycopg2_ok:
        logger.info("✅ ¡Railway PostgreSQL funciona!")
    else:
        logger.error("❌ Problemas con Railway PostgreSQL")
