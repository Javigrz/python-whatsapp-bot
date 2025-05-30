#!/usr/bin/env python3
"""
Script para generar reportes de conversación
"""
import asyncio
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import select
from sqlalchemy import func
from typing import Optional
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.settings import settings
from src.core.models import Client, Thread, Message


async def generate_conversation_report(
    client_id: int, 
    wa_id: Optional[str] = None,
    format: str = "text"
):
    """Genera un reporte de conversación para un cliente"""
    
    # Crear engine
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        # Obtener cliente
        result = await session.execute(
            select(Client).where(Client.id == client_id)
        )
        client = result.scalar_one_or_none()
        
        if not client:
            print(f"❌ Cliente con ID {client_id} no encontrado")
            return
        
        print(f"\n📊 Generando reporte para: {client.name}")
        print("="*50)
        
        # Construir query de threads
        thread_query = select(Thread).where(Thread.client_id == client_id)
        if wa_id:
            thread_query = thread_query.where(Thread.wa_id == wa_id)
        
        result = await session.execute(thread_query.order_by(Thread.created_at.desc()))
        threads = result.scalars().all()
        
        if not threads:
            print("No se encontraron conversaciones")
            return
        
        print(f"\n📱 Total de conversaciones: {len(threads)}")
        
        # Generar reporte por cada thread
        for thread in threads:
            print(f"\n{'='*50}")
            print(f"👤 Usuario WhatsApp: {thread.wa_id}")
            print(f"📅 Inicio: {thread.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🕐 Última actividad: {thread.last_message_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Obtener mensajes
            result = await session.execute(
                select(Message)
                .where(Message.thread_id == thread.id)
                .order_by(Message.created_at)
            )
            messages = result.scalars().all()
            
            print(f"💬 Total mensajes: {len(messages)}")
            print(f"\n{'-'*50}")
            
            if format == "detailed":
                # Mostrar todos los mensajes
                for msg in messages:
                    timestamp = msg.created_at.strftime('%H:%M:%S')
                    role = "👤 Usuario" if msg.role == "user" else "🤖 Asistente"
                    print(f"\n[{timestamp}] {role}:")
                    print(msg.content)
                    if msg.status and msg.role == "assistant":
                        print(f"(Estado: {msg.status})")
            else:
                # Resumen
                user_messages = len([m for m in messages if m.role == "user"])
                assistant_messages = len([m for m in messages if m.role == "assistant"])
                print(f"   👤 Mensajes del usuario: {user_messages}")
                print(f"   🤖 Respuestas del asistente: {assistant_messages}")
        
        # Estadísticas generales
        print(f"\n{'='*50}")
        print("📊 ESTADÍSTICAS GENERALES")
        print(f"{'='*50}")
        
        # Total de mensajes
        result = await session.execute(
            select(func.count(Message.id))
            .join(Thread)
            .where(Thread.client_id == client_id)
        )
        total_messages = result.scalar()
        
        print(f"💬 Total de mensajes en todas las conversaciones: {total_messages}")
        
    await engine.dispose()


async def list_clients():
    """Lista todos los clientes disponibles"""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Client).where(Client.active == True).order_by(Client.name)
        )
        clients = result.scalars().all()
        
        if not clients:
            print("No hay clientes activos")
            return
        
        print("\n📋 CLIENTES DISPONIBLES:")
        print("="*50)
        for client in clients:
            print(f"ID: {client.id} | {client.name} | {client.phone_number}")
    
    await engine.dispose()


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generar reportes de conversación')
    parser.add_argument('--list', action='store_true', help='Listar clientes disponibles')
    parser.add_argument('--client-id', type=int, help='ID del cliente')
    parser.add_argument('--wa-id', type=str, help='WhatsApp ID del usuario (opcional)')
    parser.add_argument('--format', choices=['summary', 'detailed'], default='summary', 
                       help='Formato del reporte')
    
    args = parser.parse_args()
    
    if args.list:
        await list_clients()
    elif args.client_id:
        await generate_conversation_report(
            client_id=args.client_id,
            wa_id=args.wa_id,
            format=args.format
        )
    else:
        parser.print_help()
        print("\nEjemplos de uso:")
        print("  python generate_report.py --list")
        print("  python generate_report.py --client-id 1 --format summary")
        print("  python generate_report.py --client-id 1 --wa-id +34123456789 --format detailed")


if __name__ == "__main__":
    asyncio.run(main()) 