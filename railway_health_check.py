#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la salud de WhatsApp Bot
Funciona tanto en Railway como localmente
"""
import os
import sys
import logging
import traceback
import requests
from datetime import datetime
import json
import platform
import subprocess

# Configurar logging con colores
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Colores para mejor visualización
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

logger = logging.getLogger(__name__)

def print_header(title):
    """Imprimir un encabezado formateado"""
    print(f"\n{BLUE}{'=' * 75}{RESET}")
    print(f"{BLUE}== {title.center(69)} =={RESET}")
    print(f"{BLUE}{'=' * 75}{RESET}")

def print_section(title):
    """Imprimir el título de una sección"""
    print(f"\n{BLUE}>> {title}{RESET}")

def print_success(message):
    """Imprimir un mensaje de éxito"""
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    """Imprimir un mensaje de error"""
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    """Imprimir un mensaje de advertencia"""
    print(f"{YELLOW}⚠️ {message}{RESET}")

def print_info(message):
    """Imprimir un mensaje informativo"""
    print(f"{BLUE}🔍 {message}{RESET}")

def check_environment():
    """Verificar el entorno de ejecución"""
    print_section("Verificando entorno")
    
    # Verificar si estamos en Railway
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    if railway_env:
        print_success(f"Ejecutando en Railway (entorno: {railway_env})")
    else:
        print_warning("Ejecutando localmente")
    
    # Verificar Python
    print_info(f"Python: {platform.python_version()}")
    print_info(f"Sistema: {platform.system()} {platform.release()}")
    
    # Verificar variables de entorno críticas
    critical_vars = [
        'DATABASE_URL', 'ACCESS_TOKEN', 'VERIFY_TOKEN',
        'APP_ID', 'APP_SECRET', 'OPENAI_API_KEY'
    ]
    
    for var in critical_vars:
        if os.getenv(var):
            masked_value = os.getenv(var)[:6] + "..." if os.getenv(var) else None
            print_success(f"Variable '{var}' configurada: {masked_value}")
        else:
            print_warning(f"Variable '{var}' no configurada")

def check_database():
    """Verificar la conexión a la base de datos"""
    print_section("Verificando base de datos")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print_error("DATABASE_URL no configurada")
        return False
    
    # Detectar tipo de conexión
    if 'railway.internal' in database_url:
        print_info("Usando host interno de Railway")
    elif 'proxy.rlwy.net' in database_url:
        print_info("Usando proxy externo de Railway")
    else:
        print_info("Usando base de datos personalizada")
    
    try:
        # Intentar importar la base de datos sin establecer conexión
        from sqlalchemy import create_engine, text
        
        print_success("SQLAlchemy importado correctamente")
        
        # Ahora intentar conectar
        try:
            # Intentar con diferentes modos SSL
            ssl_modes = ["require", "prefer", "disable"]
            connected = False
            
            for ssl_mode in ssl_modes:
                try:
                    db_url = add_ssl_mode(database_url, ssl_mode)
                    print_info(f"Probando conexión con sslmode={ssl_mode}")
                    
                    engine = create_engine(db_url, echo=False)
                    with engine.connect() as conn:
                        result = conn.execute(text("SELECT version();"))
                        version = result.fetchone()[0]
                        print_success(f"Conexión exitosa con sslmode={ssl_mode}")
                        print_success(f"PostgreSQL: {version[:50]}...")
                        connected = True
                        
                        try:
                            # Verificar tablas existentes
                            result = conn.execute(text(
                                """
                                SELECT table_name 
                                FROM information_schema.tables 
                                WHERE table_schema='public'
                                """
                            ))
                            tables = [row[0] for row in result]
                            print_success(f"Tablas encontradas: {', '.join(tables)}")
                        except Exception as e:
                            print_warning(f"No se pudieron listar las tablas: {e}")
                        
                        break
                except Exception as e:
                    print_warning(f"Falló con sslmode={ssl_mode}: {e}")
            
            if not connected:
                print_error("No se pudo conectar a la base de datos")
                return False
            
        except Exception as e:
            print_error(f"Error de conexión: {e}")
            return False
            
    except ImportError:
        print_error("No se pudo importar SQLAlchemy")
        return False
    
    return True

def add_ssl_mode(url, ssl_mode):
    """Agregar modo SSL a una URL de base de datos"""
    if '?' in url:
        return f"{url}&sslmode={ssl_mode}"
    else:
        return f"{url}?sslmode={ssl_mode}"

def check_api_health():
    """Verificar la salud de la API"""
    print_section("Verificando API")
    
    # Determinar la URL base
    railway_url = os.getenv('RAILWAY_SERVICE_RELEASED_SALES_BOT_URL')
    if railway_url:
        base_url = f"https://{railway_url}"
    else:
        base_url = "http://localhost:8080"
    
    print_info(f"URL base: {base_url}")
    
    try:
        # Verificar el endpoint de salud
        print_info("Probando endpoint /health...")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"API responde correctamente (status: {response.status_code})")
            print_info(f"Estado: {health_data.get('status')}")
            print_info(f"Versión: {health_data.get('version')}")
            print_info(f"Base de datos: {health_data.get('database')}")
            print_info(f"APIs: {health_data.get('apis')}")
            return True
        else:
            print_error(f"API responde con error (status: {response.status_code})")
            print_error(f"Respuesta: {response.text[:100]}...")
            return False
    except Exception as e:
        print_error(f"Error al contactar la API: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print_header("DIAGNÓSTICO DE WHATSAPP BOT")
    print_info(f"Fecha y hora: {datetime.now()}")
    
    # Verificar componentes
    environment_ok = check_environment()
    database_ok = check_database()
    api_ok = check_api_health()
    
    # Resumen
    print_header("RESUMEN")
    print_info(f"Entorno: {'✅' if environment_ok else '⚠️'}")
    print_info(f"Base de datos: {'✅' if database_ok else '❌'}")
    print_info(f"API: {'✅' if api_ok else '❌'}")
    
    # Estado general
    if database_ok and api_ok:
        print_success("El sistema está funcionando correctamente!")
        return 0
    else:
        print_error("El sistema presenta problemas. Revisa los detalles anteriores.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
