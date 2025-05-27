#!/usr/bin/env python3
"""
Script para gestionar clientes en el sistema de WhatsApp Bot.

Uso:
    python scripts/manage_clients.py add "Nombre Cliente" "+34123456789" "phone_number_id" "assistant_id"
    python scripts/manage_clients.py list
    python scripts/manage_clients.py deactivate 1
"""

import asyncio
import sys
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.models import Client
from src.core.settings import settings


async def create_client(name: str, phone_number: str, phone_number_id: str, assistant_id: str):
    """Crear un nuevo cliente"""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with AsyncSession(engine) as session:
        # Verificar si ya existe
        result = await session.execute(
            select(Client).where(Client.phone_number_id == phone_number_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"❌ Ya existe un cliente con phone_number_id: {phone_number_id}")
            return
        
        # Crear nuevo cliente
        client = Client(
            name=name,
            phone_number=phone_number,
            phone_number_id=phone_number_id,
            assistant_id=assistant_id,
            active=True
        )
        
        session.add(client)
        await session.commit()
        await session.refresh(client)
        
        print(f"✅ Cliente creado exitosamente:")
        print(f"   ID: {client.id}")
        print(f"   Nombre: {client.name}")
        print(f"   Teléfono: {client.phone_number}")
        print(f"   Phone Number ID: {client.phone_number_id}")
        print(f"   Assistant ID: {client.assistant_id}")


async def list_clients():
    """Listar todos los clientes"""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Client))
        clients = result.scalars().all()
        
        if not clients:
            print("📋 No hay clientes registrados")
            return
        
        print("\n📋 LISTA DE CLIENTES:")
        print("-" * 80)
        print(f"{'ID':<5} {'Nombre':<20} {'Teléfono':<15} {'Phone Number ID':<20} {'Activo':<8}")
        print("-" * 80)
        
        for client in clients:
            status = "✅ Sí" if client.active else "❌ No"
            print(f"{client.id:<5} {client.name:<20} {client.phone_number:<15} {client.phone_number_id:<20} {status:<8}")
        
        print("-" * 80)
        print(f"Total: {len(clients)} clientes\n")


async def deactivate_client(client_id: int):
    """Desactivar un cliente"""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Client).where(Client.id == client_id)
        )
        client = result.scalar_one_or_none()
        
        if not client:
            print(f"❌ No se encontró cliente con ID: {client_id}")
            return
        
        client.active = False
        client.updated_at = datetime.utcnow()
        
        await session.commit()
        print(f"✅ Cliente '{client.name}' desactivado exitosamente")


async def activate_client(client_id: int):
    """Activar un cliente"""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Client).where(Client.id == client_id)
        )
        client = result.scalar_one_or_none()
        
        if not client:
            print(f"❌ No se encontró cliente con ID: {client_id}")
            return
        
        client.active = True
        client.updated_at = datetime.utcnow()
        
        await session.commit()
        print(f"✅ Cliente '{client.name}' activado exitosamente")


def print_usage():
    print("""
Uso: python scripts/manage_clients.py [comando] [argumentos]

Comandos disponibles:
    add <nombre> <telefono> <phone_number_id> <assistant_id>  - Agregar nuevo cliente
    list                                                       - Listar todos los clientes
    deactivate <id>                                           - Desactivar un cliente
    activate <id>                                             - Activar un cliente
    
Ejemplos:
    python scripts/manage_clients.py add "Restaurante La Plaza" "+34666777888" "631261586727899" "asst_abc123"
    python scripts/manage_clients.py list
    python scripts/manage_clients.py deactivate 1
    """)


async def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) != 6:
            print("❌ Error: El comando 'add' requiere 4 argumentos")
            print("   Uso: add <nombre> <telefono> <phone_number_id> <assistant_id>")
            return
        
        await create_client(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    
    elif command == "list":
        await list_clients()
    
    elif command == "deactivate":
        if len(sys.argv) != 3:
            print("❌ Error: El comando 'deactivate' requiere el ID del cliente")
            return
        
        try:
            client_id = int(sys.argv[2])
            await deactivate_client(client_id)
        except ValueError:
            print("❌ Error: El ID debe ser un número")
    
    elif command == "activate":
        if len(sys.argv) != 3:
            print("❌ Error: El comando 'activate' requiere el ID del cliente")
            return
        
        try:
            client_id = int(sys.argv[2])
            await activate_client(client_id)
        except ValueError:
            print("❌ Error: El ID debe ser un número")
    
    else:
        print(f"❌ Comando desconocido: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main()) 