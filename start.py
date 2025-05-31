#!/usr/bin/env python3
"""
Script de inicio para Railway
"""
import os
import sys
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Verificar que podemos importar la aplicación
        logger.info("Iniciando aplicación...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
        
        # Obtener puerto
        port = int(os.getenv("PORT", "8000"))
        logger.info(f"Puerto configurado: {port}")
        
        # Importar uvicorn y la app
        try:
            import uvicorn
            logger.info("✅ uvicorn importado correctamente")
        except ImportError as e:
            logger.error(f"❌ Error importando uvicorn: {e}")
            sys.exit(1)
        
        try:
            from src.main import app
            logger.info("✅ Aplicación importada correctamente")
        except ImportError as e:
            logger.error(f"❌ Error importando aplicación: {e}")
            logger.error("Estructura de directorios:")
            for root, dirs, files in os.walk("."):
                level = root.replace(".", "").count(os.sep)
                indent = " " * 2 * level
                logger.error(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files:
                    logger.error(f"{subindent}{file}")
            sys.exit(1)
        
        # Iniciar servidor
        logger.info(f"Iniciando servidor en 0.0.0.0:{port}")
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            workers=1,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
