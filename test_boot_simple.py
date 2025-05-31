#!/usr/bin/env python3
"""
Test simple para verificar que boot.py funciona correctamente
"""
import subprocess
import sys
import os

def test_boot():
    print("🧪 Testing boot.py...")
    
    # Configurar entorno como Railway
    env = os.environ.copy()
    env.update({
        'PORT': '8000',
        'PYTHONUNBUFFERED': '1'
    })
    
    try:
        # Ejecutar boot.py por 2 segundos para ver los logs
        result = subprocess.run(
            [sys.executable, 'boot.py'],
            env=env,
            capture_output=True,
            text=True,
            timeout=2
        )
    except subprocess.TimeoutExpired as e:
        # Timeout esperado, mostrar output
        print("✅ Boot script inició correctamente (timeout esperado)")
        if e.stdout:
            print("📋 STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("📋 STDERR:")
            print(e.stderr)
        return True
    except Exception as e:
        print(f"❌ Error ejecutando boot.py: {e}")
        return False
    
    # Si termina sin timeout, algo salió mal
    print("❌ Boot script terminó inesperadamente")
    print("📋 STDOUT:")
    print(result.stdout)
    print("📋 STDERR:")
    print(result.stderr)
    print(f"📋 Return code: {result.returncode}")
    return False

if __name__ == "__main__":
    success = test_boot()
    print("\n" + "="*50)
    if success:
        print("🎉 boot.py está funcionando correctamente!")
        print("✅ Listo para Railway deployment")
    else:
        print("❌ boot.py tiene problemas")
        print("🔧 Revisa los errores arriba")
    print("="*50)
