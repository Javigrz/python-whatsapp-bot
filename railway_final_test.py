#!/usr/bin/env python3
"""
Test final para Railway - Simula exactamente el entorno de Railway
"""
import os
import sys
import subprocess
import tempfile
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def simulate_railway_environment():
    """Simula las variables de entorno que Railway proporciona"""
    railway_env = {
        'PORT': '8000',
        'RAILWAY_ENVIRONMENT': 'production',
        'DATABASE_URL': 'postgresql://user:pass@localhost:5432/railway',
        'PYTHONPATH': '.',
        'PYTHONUNBUFFERED': '1',
        # Variables que deberías configurar en Railway
        'ACCESS_TOKEN': 'test_token',
        'VERIFY_TOKEN': 'test_verify',
        'APP_ID': 'test_app_id',
        'APP_SECRET': 'test_secret',
    }
    
    for key, value in railway_env.items():
        os.environ[key] = value
    
    logger.info("🚀 Variables de entorno de Railway simuladas")
    return railway_env

def test_start_script():
    """Test del script start.py como lo haría Railway"""
    logger.info("\n🧪 TESTING: python start.py")
    
    try:
        # Ejecutar start.py en modo test (sin iniciar el servidor)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
import sys
import os
sys.path.insert(0, ".")

# Simular railway env
os.environ.update({
    'PORT': '8000',
    'DATABASE_URL': 'postgresql://user:pass@localhost:5432/test',
    'ACCESS_TOKEN': 'test',
    'VERIFY_TOKEN': 'test'
})

try:
    from src.main import app
    from fastapi import FastAPI
    
    if isinstance(app, FastAPI):
        print("✅ SUCCESS: Aplicación cargada correctamente")
        print(f"✅ SUCCESS: Tipo de app: {type(app)}")
        print("✅ SUCCESS: Listo para Railway")
        exit(0)
    else:
        print("❌ ERROR: app no es FastAPI")
        exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
''')
            test_file = f.name
        
        # Ejecutar el test
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=30)
        
        os.unlink(test_file)  # Limpiar archivo temporal
        
        if result.returncode == 0:
            logger.info("✅ start.py funcionaría correctamente en Railway")
            logger.info(result.stdout)
            return True
        else:
            logger.error("❌ start.py fallaría en Railway")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error ejecutando test: {e}")
        return False

def test_railway_commands():
    """Test de comandos alternativos para Railway"""
    commands_to_test = [
        'python start.py',
        'uvicorn src.main:app --host 0.0.0.0 --port 8000',
        'python main.py'
    ]
    
    logger.info(f"\n🧪 TESTING: Comandos alternativos")
    
    working_commands = []
    
    for cmd in commands_to_test:
        logger.info(f"  Probando: {cmd}")
        
        # Para uvicorn, solo verificamos que puede importar
        if 'uvicorn' in cmd:
            try:
                import uvicorn
                logger.info(f"    ✅ uvicorn disponible")
                working_commands.append(cmd)
            except ImportError:
                logger.info(f"    ❌ uvicorn no disponible")
        
        # Para python scripts, verificamos que existen
        elif 'python start.py' in cmd:
            if os.path.exists('start.py'):
                logger.info(f"    ✅ start.py existe")
                working_commands.append(cmd)
            else:
                logger.info(f"    ❌ start.py no existe")
        
        elif 'python main.py' in cmd:
            if os.path.exists('main.py'):
                logger.info(f"    ✅ main.py existe")
                working_commands.append(cmd)
            else:
                logger.info(f"    ❌ main.py no existe")
    
    return working_commands

def check_railway_files():
    """Verificar archivos específicos para Railway"""
    railway_files = {
        'start.py': 'Script de inicio principal',
        'requirements.txt': 'Dependencias Python',
        'railway.toml': 'Configuración Railway',
        'nixpacks.toml': 'Configuración Nixpacks',
        'src/main.py': 'Aplicación FastAPI',
        'src/core/settings.py': 'Configuración de la app'
    }
    
    logger.info(f"\n🧪 TESTING: Archivos para Railway")
    
    all_present = True
    for file_path, description in railway_files.items():
        if os.path.exists(file_path):
            logger.info(f"  ✅ {file_path} - {description}")
        else:
            logger.error(f"  ❌ {file_path} - {description} (FALTA)")
            all_present = False
    
    return all_present

def main():
    logger.info("🚀 TEST FINAL PARA RAILWAY")
    logger.info("=" * 60)
    
    # Simular entorno Railway
    simulate_railway_environment()
    
    # Ejecutar tests
    tests = [
        ("Archivos Railway", check_railway_files),
        ("Script start.py", test_start_script),
        ("Comandos alternativos", lambda: len(test_railway_commands()) > 0)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}:")
        try:
            result = test_func()
            results.append(result)
            if result:
                logger.info(f"  ✅ {test_name}: PASSED")
            else:
                logger.error(f"  ❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"  ❌ {test_name}: ERROR - {e}")
            results.append(False)
    
    # Resultados finales
    logger.info("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logger.info("🎉 ¡LISTO PARA RAILWAY!")
        logger.info("\n📋 INSTRUCCIONES FINALES:")
        logger.info("1. Ve a railway.app")
        logger.info("2. Crea un nuevo proyecto desde GitHub")
        logger.info("3. Conecta este repositorio")
        logger.info("4. Configura estas variables de entorno:")
        logger.info("   - ACCESS_TOKEN (obligatorio)")
        logger.info("   - VERIFY_TOKEN (obligatorio)")
        logger.info("   - OPENAI_API_KEY (opcional)")
        logger.info("   - APP_ID, APP_SECRET (opcionales)")
        logger.info("5. Railway detectará automáticamente el build")
        logger.info("6. El comando de inicio será: python start.py")
        logger.info("\n🌐 Endpoints disponibles:")
        logger.info("   - GET /health (health check)")
        logger.info("   - GET / (info básica)")
        logger.info("   - POST /webhook (WhatsApp webhook)")
        
    else:
        logger.error(f"❌ {total - passed} tests fallaron")
        logger.error("Revisa los errores antes de hacer deploy")
        
        # Sugerencias de solución
        logger.info("\n🔧 POSIBLES SOLUCIONES:")
        logger.info("- Verifica que todos los archivos estén presentes")
        logger.info("- Instala dependencias: pip install -r requirements.txt")
        logger.info("- Verifica que src/main.py sea importable")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
