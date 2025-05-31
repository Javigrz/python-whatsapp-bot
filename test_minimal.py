#!/usr/bin/env python3
"""
Test ultra simple para Railway
"""
import os
import sys

def test_minimal_app():
    """Test de la aplicación mínima"""
    try:
        os.environ['PORT'] = '8000'
        
        # Test 1: Importar FastAPI
        from fastapi import FastAPI
        print("✅ FastAPI importado")
        
        # Test 2: Importar uvicorn
        import uvicorn
        print("✅ uvicorn importado")
        
        # Test 3: Importar aplicación mínima
        from src.main_minimal import app
        print("✅ Aplicación mínima importada")
        
        # Test 4: Verificar que es FastAPI
        if isinstance(app, FastAPI):
            print("✅ app es una instancia de FastAPI")
        else:
            print("❌ app NO es FastAPI")
            return False
        
        # Test 5: Verificar puerto
        port = int(os.getenv('PORT', '8000'))
        print(f"✅ Puerto: {port}")
        
        print("\n🎉 ¡CONFIGURACIÓN MÍNIMA LISTA!")
        print("✅ Usar: python start_simple.py")
        print("✅ O en Railway Settings: python start_simple.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_minimal_app():
        print("\n🚀 LISTO PARA RAILWAY CON CONFIGURACIÓN MÍNIMA")
        sys.exit(0)
    else:
        print("\n❌ Configuración mínima falló")
        sys.exit(1)
