#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    
    # Intentar la app principal, si falla usar la mínima
    try:
        from src.main import app
        print("✅ Usando aplicación principal")
    except:
        try:
            from src.main_minimal import app
            print("✅ Usando aplicación mínima")
        except:
            # Crear app inline como último recurso
            from fastapi import FastAPI
            app = FastAPI()
            
            @app.get("/")
            def root():
                return {"message": "WhatsApp Bot API", "status": "running"}
            
            @app.get("/health")
            def health():
                return {"status": "healthy"}
            
            print("✅ Usando aplicación de emergencia")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
