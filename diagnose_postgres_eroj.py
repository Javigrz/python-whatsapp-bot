#!/usr/bin/env python3
"""
Script de diagnóstico para probar la conexión con el nuevo servicio PostgreSQL-Eroj
"""
import os
import psycopg2
import logging
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Colores para la terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def test_postgres_eroj_connection():
    """Probar la conexión con el servicio Postgres-Eroj"""
    # Obtener las variables de entorno para Postgres-Eroj
    db_url = os.getenv('DATABASE_URL')
    db_host = os.getenv('POSTGRES_HOST', 'postgres-eroj.railway.internal')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB', 'railway')
    
    if not db_password:
        logger.error(f"{RED}❌ No se encontró POSTGRES_PASSWORD en las variables de entorno{RESET}")
        return False
    
    logger.info(f"{BLUE}🔍 Diagnosticando conexión a PostgreSQL-Eroj...{RESET}")
    
    # Intentar conexión directa con psycopg2
    logger.info(f"{BLUE}1. Probando conexión directa con psycopg2...{RESET}")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            connect_timeout=30
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"{GREEN}✅ Conexión directa exitosa: {version[0][:50]}...{RESET}")
        
        cursor.close()
        conn.close()
        direct_success = True
    except Exception as e:
        logger.error(f"{RED}❌ Conexión directa falló: {str(e)}{RESET}")
        direct_success = False
    
    # Intentar conexión con SQLAlchemy
    logger.info(f"{BLUE}2. Probando conexión con SQLAlchemy...{RESET}")
    
    if db_url:
        url_to_use = db_url
        logger.info(f"{BLUE}   Usando DATABASE_URL de las variables de entorno{RESET}")
    else:
        url_to_use = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"{BLUE}   Construyendo URL desde variables individuales{RESET}")
    
    # Intentar con diferentes modos SSL
    ssl_modes = ["require", "prefer", "allow", "disable"]
    sqlalchemy_success = False
    
    for ssl_mode in ssl_modes:
        try:
            # Construir URL con SSL específico
            if '?' in url_to_use:
                test_url = f"{url_to_use}&sslmode={ssl_mode}"
            else:
                test_url = f"{url_to_use}?sslmode={ssl_mode}"
                
            logger.info(f"{BLUE}   Probando con sslmode={ssl_mode}...{RESET}")
            
            engine = create_engine(
                test_url,
                echo=False,
                pool_pre_ping=True,
                connect_args={
                    "application_name": "diagnostic-test",
                    "connect_timeout": 30
                }
            )
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                
                logger.info(f"{GREEN}✅ Conexión SQLAlchemy exitosa con sslmode={ssl_mode}{RESET}")
                logger.info(f"{GREEN}   PostgreSQL: {version[:50]}...{RESET}")
                
                # Probar una operación simple
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS test_diagnostic (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                conn.execute(text("INSERT INTO test_diagnostic DEFAULT VALUES;"))
                count_result = conn.execute(text("SELECT COUNT(*) FROM test_diagnostic;"))
                count = count_result.fetchone()[0]
                logger.info(f"{GREEN}✅ Operaciones básicas exitosas. Registros en tabla de prueba: {count}{RESET}")
                
                sqlalchemy_success = True
                break
        except Exception as e:
            logger.warning(f"{YELLOW}⚠️ Error con sslmode={ssl_mode}: {str(e)[:100]}{RESET}")
    
    if sqlalchemy_success:
        logger.info(f"{GREEN}✅ Diagnóstico completo: Conexión a PostgreSQL-Eroj exitosa{RESET}")
    else:
        logger.error(f"{RED}❌ Diagnóstico completo: Todos los intentos de conexión fallaron{RESET}")
    
    return direct_success or sqlalchemy_success

if __name__ == "__main__":
    success = test_postgres_eroj_connection()
    if success:
        logger.info(f"{GREEN}✅ La conexión a PostgreSQL-Eroj está funcionando correctamente!{RESET}")
    else:
        logger.error(f"{RED}❌ Falló la conexión a PostgreSQL-Eroj. Revisa la configuración y los logs para más detalles.{RESET}")
