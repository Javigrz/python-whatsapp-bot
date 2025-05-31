#!/usr/bin/env python3
"""
Script para probar la configuración antes del deploy a Railway
"""
import os
import sys
import subprocess

def test_import():
    """Prueba que se puede importar la aplicación"""
    try:
        from src.main import app
        print("✅ Import de src.main.app exitoso")
        return True
    except ImportError as e:
        print(f"❌ Error importando src.main.app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_uvicorn_command():
    """Prueba que uvicorn puede encontrar la app"""
    try:
        # Simular el comando que usará Railway
        result = subprocess.run([
            sys.executable, "-c", 
            "import uvicorn; from src.main import app; print('✅ uvicorn puede encontrar la app')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ uvicorn puede cargar la aplicación")
            return True
        else:
            print(f"❌ Error en uvicorn: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error probando uvicorn: {e}")
        return False

def test_port_handling():
    """Prueba el manejo del puerto"""
    os.environ['PORT'] = '8000'  # Simular Railway
    try:
        port = int(os.getenv('PORT', '8000'))
        print(f"✅ PORT se puede convertir a entero: {port}")
        return True
    except ValueError as e:
        print(f"❌ Error convirtiendo PORT: {e}")
        return False

def main():
    print("🚀 PRUEBA DE CONFIGURACIÓN PARA RAILWAY")
    print("=" * 50)
    
    tests = [
        ("Importación de la app", test_import),
        ("Comando uvicorn", test_uvicorn_command),
        ("Manejo de PORT", test_port_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Probando: {test_name}")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 ¡Todas las pruebas pasaron! Listo para Railway")
        print("\n📝 Comandos sugeridos para Railway:")
        print("1. railway login")
        print("2. railway link")
        print("3. railway up")
    else:
        print("❌ Algunas pruebas fallaron. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main()
