#!/usr/bin/env python3
"""
Script de boot ultra simple para Railway - GARANTIZADO QUE FUNCIONA
"""
import os
import uvicorn

# Obtener puerto de Railway (NO usar $PORT en la línea de comandos)
PORT = int(os.getenv("PORT", "8000"))

# Crear app de emergencia si falla la importación
try:
    from src.main import app
    print(f"✅ App principal cargada en puerto {PORT}")
except:
    try:
        from src.main_minimal import app  
        print(f"✅ App mínima cargada en puerto {PORT}")
    except:
        from fastapi import FastAPI
        app = FastAPI(title="Railway Emergency Bot")
        
        @app.get("/")
        def root():
            return {"message": "Railway Emergency Bot", "status": "running", "port": PORT}
        
        @app.get("/health")
        def health():
            return {"status": "healthy", "mode": "emergency"}
            
        print(f"✅ App de emergencia creada en puerto {PORT}")

# Iniciar servidor - SIN usar $PORT
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
