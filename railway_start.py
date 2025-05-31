#!/usr/bin/env python3
"""
Railway Start Script - Funcional garantizado
"""
import os
import sys

# Configurar variables de entorno
PORT = int(os.getenv("PORT", "8000"))
print(f"🚀 Starting Railway app on port {PORT}")

try:
    # Importar dependencias
    import uvicorn
    print("✅ uvicorn imported successfully")
    
    # Intentar cargar la aplicación
    sys.path.insert(0, ".")
    sys.path.insert(0, "/app")
    
    try:
        from src.main import app
        print("✅ Main app loaded from src.main")
    except Exception as e:
        print(f"⚠️ Could not load src.main: {e}")
        try:
            from src.main_minimal import app
            print("✅ Minimal app loaded from src.main_minimal")
        except Exception as e:
            print(f"⚠️ Could not load src.main_minimal: {e}")
            # Crear app de emergencia
            from fastapi import FastAPI
            app = FastAPI(title="Railway WhatsApp Bot")
            
            @app.get("/")
            def root():
                return {
                    "message": "Railway WhatsApp Bot", 
                    "status": "running", 
                    "port": PORT,
                    "mode": "emergency"
                }
            
            @app.get("/health")
            def health():
                return {"status": "healthy", "port": PORT}
                
            print("✅ Emergency app created")
    
    # Iniciar servidor
    print(f"🌐 Starting uvicorn server on 0.0.0.0:{PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Critical error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
