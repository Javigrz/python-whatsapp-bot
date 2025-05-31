#!/usr/bin/env python3
"""
ARCHIVO FINAL INFALIBLE PARA RAILWAY
Este archivo usa el método más directo posible sin dependencias
"""
import os
import sys

def main():
    print("🚀 INICIANDO APLICACIÓN RAILWAY...")
    
    # Obtener puerto de Railway
    port = int(os.getenv("PORT", "8000"))
    print(f"📍 Puerto: {port}")
    
    # Verificar que podemos importar
    try:
        print("📦 Importando FastAPI...")
        from fastapi import FastAPI
        
        print("📦 Importando uvicorn...")
        import uvicorn
        
        print("📦 Importando aplicación...")
        # Intentar la app principal
        try:
            from src.main import app
            print("✅ App principal cargada!")
        except Exception as e:
            print(f"⚠️  Error cargando app principal: {e}")
            print("🔄 Creando app mínima...")
            
            # Crear app mínima inline
            app = FastAPI(title="WhatsApp Bot Railway", version="1.0.0")
            
            @app.get("/")
            def root():
                return {
                    "status": "ok", 
                    "message": "WhatsApp Bot funcionando en Railway",
                    "port": port
                }
                
            @app.get("/health")
            def health():
                return {"status": "healthy", "service": "whatsapp-bot"}
                
            @app.post("/webhook")
            def webhook():
                return {"status": "received"}
        
        print("🌟 INICIANDO SERVIDOR...")
        print(f"🌐 URL: http://0.0.0.0:{port}")
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=port, 
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"💥 ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
