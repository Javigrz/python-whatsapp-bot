#!/usr/bin/env python3
"""
Test para verificar que uvicorn puede importar la aplicación
"""
import sys
import os

# Simular variables de entorno como Railway
os.environ.update({
    'PORT': '8000',
    'ACCESS_TOKEN': 'test_token',
    'VERIFY_TOKEN': 'test_token',
    'PYTHONPATH': '.'
})

try:
    # Intentar importar la aplicación
    print("Importando src.main:app...")
    from src.main import app
    from fastapi import FastAPI
    
    if isinstance(app, FastAPI):
        print("✅ SUCCESS: Aplicación importada correctamente")
        print(f"✅ Tipo: {type(app)}")
        print("✅ uvicorn puede usar esta aplicación")
        
        # Verificar que tiene endpoints
        routes = [route.path for route in app.routes]
        print(f"✅ Rutas disponibles: {routes}")
        
    else:
        print("❌ ERROR: app no es una instancia de FastAPI")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR importando aplicación: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ Test completo - Listo para uvicorn")
