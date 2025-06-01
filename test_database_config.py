#!/usr/bin/env python3
"""
Test simple de la configuración de base de datos actualizada
"""
import os
import sys
import logging

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_configuration():
    """Probar la configuración de base de datos actualizada"""
    
    logger.info("🚀 Probando configuración de base de datos actualizada")
    
    try:
        # Probar inicialización
        success = db_manager.initialize()
        
        if not success:
            logger.error("❌ Falló la inicialización")
            return False
        
        # Probar health check
        health = db_manager.health_check()
        
        if not health:
            logger.error("❌ Falló el health check")
            return False
        
        # Probar sesión
        session = db_manager.get_session()
        session.close()
        
        logger.info("✅ ¡Configuración de base de datos exitosa!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False
    
    finally:
        # Limpiar
        try:
            db_manager.close()
        except:
            pass

if __name__ == "__main__":
    success = test_database_configuration()
    
    if success:
        logger.info("✅ Base de datos configurada correctamente")
    else:
        logger.error("❌ Problemas con la configuración de base de datos")
