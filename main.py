from fastapi import FastAPI, HTTPException
from database import init_db
import logging
from typing import Dict

logger = logging.getLogger(__name__)
app = FastAPI()

# Variable global para tracking del estado
app.state.database_ready = False

@app.on_event("startup")
async def on_startup():
    try:
        app.state.db = await init_db()
        app.state.database_ready = True
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        # No levantamos error aquí para permitir que la app inicie

@app.get("/health")
async def health_check() -> Dict:
    if not app.state.database_ready:
        raise HTTPException(
            status_code=503,
            detail="Database not ready"
        )
    return {
        "status": "healthy",
        "database": "connected"
    }

# ...existing code...