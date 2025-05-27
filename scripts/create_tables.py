#!/usr/bin/env python3
"""Script para crear las tablas en la base de datos"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.settings import settings
from src.core.models import Agent, Client, Thread


async def create_tables():
    """Crear todas las tablas"""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Crear todas las tablas
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("✅ Tablas creadas exitosamente")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables()) 