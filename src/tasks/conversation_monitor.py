from datetime import datetime, timedelta
import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from celery import shared_task
import jinja2
import os
from resend import Resend

from src.core.models import Thread, Client, Message
from src.core.settings import settings
from src.core.openai_client import openai_client

# Configuración de Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend = Resend(RESEND_API_KEY)

# Plantilla HTML para el reporte
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; }
        .assistant { background: #f1f8e9; }
        .timestamp { color: #666; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Reporte de Conversación - {{ client.name }}</h2>
        <p>Cliente: {{ client.name }}</p>
        <p>Usuario WhatsApp: {{ thread.wa_id }}</p>
        <p>Fecha inicio: {{ thread.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        <p>Última actividad: {{ thread.last_message_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        <p>Total mensajes: {{ messages|length }}</p>
    </div>
    
    <div class="messages">
        {% for msg in messages %}
        <div class="message {{ msg.role }}">
            <div class="timestamp">{{ msg.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</div>
            <div class="content">{{ msg.content }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

async def generate_report_html(client: Client, thread: Thread, messages: list[Message]) -> str:
    """Genera el HTML del reporte usando una plantilla Jinja2"""
    template = jinja2.Template(REPORT_TEMPLATE)
    return template.render(
        client=client,
        thread=thread,
        messages=messages
    )

async def send_report_email(client: Client, thread: Thread, messages: list[Message]):
    """Envía el reporte por email usando Resend"""
    if not RESEND_API_KEY:
        print("⚠️ No se configuró la API key de Resend. No se enviará el email.")
        return

    try:
        html_content = await generate_report_html(client, thread, messages)
        
        params = {
            "from": "Released Bot <report@released.es>",  # Cambiar a tu dominio verificado
            "to": client.host_email,
            "subject": f"Reporte de Conversación - {client.name} - {thread.wa_id}",
            "html": html_content
        }
        
        response = resend.emails.send(params)
        print(f"✅ Reporte enviado a {client.host_email} (ID: {response['id']})")
        
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")

async def close_conversation(thread: Thread, client: Client):
    """Cierra una conversación, genera reporte y elimina datos"""
    try:
        # 1. Obtener todos los mensajes
        engine = create_async_engine(settings.database_url)
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(Message)
                .where(Message.thread_id == thread.id)
                .order_by(Message.created_at)
            )
            messages = result.scalars().all()
            
            # 2. Generar y enviar reporte
            await send_report_email(client, thread, messages)
            
            # 3. Cerrar thread en OpenAI
            await openai_client.close_thread(thread.thread_id)
            
            # 4. Eliminar mensajes y thread de la base de datos
            for message in messages:
                await session.delete(message)
            await session.delete(thread)
            await session.commit()
            
            print(f"✅ Conversación cerrada y reporte generado para {thread.wa_id}")
            
    except Exception as e:
        print(f"❌ Error cerrando conversación: {str(e)}")
    finally:
        await engine.dispose()

@shared_task
def check_inactive_conversations():
    """Tarea Celery que verifica conversaciones inactivas"""
    engine = create_async_engine(settings.database_url)
    
    async def _check():
        async with AsyncSession(engine) as session:
            # Buscar threads inactivos por más de 5 minutos
            # inactive_time = datetime.utcnow() - timedelta(minutes=5)
            inactive_time = datetime.utcnow() - timedelta(seconds=10)
            result = await session.execute(
                select(Thread)
                .where(Thread.last_message_at < inactive_time)
                .join(Client)
                .where(Client.active == True)
            )
            inactive_threads = result.scalars().all()
            
            for thread in inactive_threads:
                # Obtener el cliente asociado
                client_result = await session.execute(
                    select(Client).where(Client.id == thread.client_id)
                )
                client = client_result.scalar_one_or_none()
                
                if client:
                    await close_conversation(thread, client)
    
    # Ejecutar la función asíncrona
    asyncio.run(_check())
    engine.dispose()

# Configurar la tarea para que se ejecute cada minuto
check_inactive_conversations.apply_async(countdown=60)  # Primera ejecución en 1 minuto 