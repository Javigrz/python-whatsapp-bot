#!/usr/bin/env python3
"""
Script de diagnóstico completo para Railway
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    logger.info(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Se requiere Python 3.8+")
        return False
    return True

def check_file_structure():
    """Verificar estructura de archivos"""
    required_files = [
        'start.py',
        'requirements.txt',
        'src/main.py',
        'src/core/settings.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    logger.info("✅ Estructura de archivos correcta")
    return True

def check_dependencies():
    """Verificar dependencias básicas"""
    try:
        import fastapi
        logger.info(f"✅ FastAPI {fastapi.__version__}")
    except ImportError:
        logger.error("❌ FastAPI no encontrado")
        return False
    
    try:
        import uvicorn
        logger.info(f"✅ Uvicorn {uvicorn.__version__}")
    except ImportError:
        logger.error("❌ Uvicorn no encontrado")
        return False
    
    try:
        import pydantic
        logger.info(f"✅ Pydantic {pydantic.__version__}")
    except ImportError:
        logger.error("❌ Pydantic no encontrado")
        return False
    
    return True

def check_settings():
    """Verificar configuración"""
    try:
        from src.core.settings import settings
        logger.info("✅ Settings importado correctamente")
        
        # Verificar configuraciones críticas
        if hasattr(settings, 'database_url') and settings.database_url:
            logger.info("✅ DATABASE_URL configurada")
        else:
            logger.warning("⚠️ DATABASE_URL no configurada")
        
        if hasattr(settings, 'port'):
            logger.info(f"✅ Puerto configurado: {settings.port}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error en settings: {e}")
        return False

def check_app_import():
    """Verificar que se puede importar la aplicación"""
    try:
        from src.main import app
        logger.info("✅ Aplicación importada correctamente")
        
        # Verificar que es una instancia de FastAPI
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            logger.info("✅ app es una instancia válida de FastAPI")
            return True
        else:
            logger.error("❌ app no es una instancia de FastAPI")
            return False
    except Exception as e:
        logger.error(f"❌ Error importando aplicación: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def simulate_railway_env():
    """Simular variables de entorno de Railway"""
    # Simular PORT de Railway
    os.environ['PORT'] = '8000'
    
    # Simular DATABASE_URL de Railway (PostgreSQL)
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db'
    
    logger.info("🔧 Variables de entorno de Railway simuladas")

def check_port_handling():
    """Verificar manejo del puerto"""
    try:
        port = int(os.getenv('PORT', '8000'))
        logger.info(f"✅ Puerto manejado correctamente: {port}")
        return True
    except ValueError as e:
        logger.error(f"❌ Error con el puerto: {e}")
        return False

def main():
    logger.info("🚀 DIAGNÓSTICO COMPLETO PARA RAILWAY")
    logger.info("=" * 60)
    
    # Simular entorno de Railway
    simulate_railway_env()
    
    tests = [
        ("Versión de Python", check_python_version),
        ("Estructura de archivos", check_file_structure),
        ("Dependencias básicas", check_dependencies),
        ("Configuración (settings)", check_settings),
        ("Manejo de puerto", check_port_handling),
        ("Importación de la app", check_app_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            logger.error(f"❌ Error en {test_name}: {e}")
            results.append(False)
    
    logger.info("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logger.info("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        logger.info("✅ Listo para deploy en Railway")
        logger.info("\n📝 Comandos para Railway:")
        logger.info("1. railway login")
        logger.info("2. railway link [tu-proyecto]")
        logger.info("3. railway up")
        logger.info("\n🔧 Configuración recomendada:")
        logger.info("- Start Command: python start.py")
        logger.info("- Variables de entorno necesarias:")
        logger.info("  * ACCESS_TOKEN (Meta)")
        logger.info("  * VERIFY_TOKEN")
        logger.info("  * OPENAI_API_KEY (opcional)")
        logger.info("  * DATABASE_URL (automática en Railway)")
        
    else:
        logger.error(f"❌ {total - passed} pruebas fallaron de {total}")
        logger.error("Revisa los errores arriba antes de hacer deploy")
        sys.exit(1)

if __name__ == "__main__":
    main()
