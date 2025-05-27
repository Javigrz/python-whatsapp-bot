#!/usr/bin/env python
"""
Worker de Celery para procesar tareas asíncronas
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tasks import celery

if __name__ == '__main__':
    celery.start() 