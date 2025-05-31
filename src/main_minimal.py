"""
Aplicación FastAPI mínima para Railway
"""
from fastapi import FastAPI
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Crea aplicación FastAPI mínima"""
    app = FastAPI(
        title="WhatsApp Bot API",
        version="1.0.0",
        description="Bot de WhatsApp para Railway"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "WhatsApp Bot API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "version": "1.0.0"
        }
    
    @app.post("/webhook")
    async def webhook():
        return {"message": "Webhook endpoint"}
    
    logger.info("✅ Aplicación FastAPI mínima creada")
    return app

# Crear aplicación
app = create_app()
