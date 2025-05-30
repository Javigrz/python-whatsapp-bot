from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from src.core.settings import settings
from src.core.openai_client import get_answer
from src.core.meta_client import send_message
from src.core.models import Client, Thread, Message
from src.core.database import get_sync_session
from sqlmodel import select
import asyncio
import time
from datetime import datetime

# Crear instancia de Celery
celery = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configuración de Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery.task(
    acks_late=True,
    max_retries=3,
    default_retry_delay=5,
    retry_backoff=True,
    retry_backoff_max=60
)
def handle_message(agent_id: str, phone_number_id: str, wa_id: str, text: str):
    """
    Procesa un mensaje de WhatsApp y envía la respuesta.
    
    Args:
        agent_id: ID del assistant de OpenAI
        phone_number_id: ID del número de WhatsApp Business
        wa_id: ID del remitente (número de WhatsApp del usuario)
        text: Texto del mensaje recibido
    """
    try:
        # Obtener o crear thread en la base de datos
        with get_sync_session() as session:
            # Buscar el cliente
            result = session.exec(
                select(Client).where(
                    Client.phone_number_id == phone_number_id,
                    Client.active == True
                )
            )
            client = result.first()
            
            # Buscar o crear thread
            result = session.exec(
                select(Thread).where(
                    Thread.wa_id == wa_id,
                    Thread.client_id == client.id if client else None
                )
            )
            thread = result.first()
            
            if not thread:
                # Crear nuevo thread
                thread = Thread(
                    wa_id=wa_id,
                    thread_id=wa_id,  # Usamos wa_id como thread_id para simplificar
                    client_id=client.id if client else None
                )
                session.add(thread)
                session.commit()
                session.refresh(thread)
            
            # Guardar mensaje del usuario
            user_message = Message(
                thread_id=thread.id,
                role="user",
                content=text,
                wa_id=wa_id,
                phone_number_id=phone_number_id
            )
            session.add(user_message)
            session.commit()
        
        # Obtener respuesta de OpenAI
        # Usar wa_id como conversation_id para mantener el contexto por usuario
        answer = get_answer(agent_id, text, conversation_id=wa_id)
        
        # Guardar respuesta del assistant
        with get_sync_session() as session:
            assistant_message = Message(
                thread_id=thread.id,
                role="assistant",
                content=answer,
                wa_id=wa_id,
                phone_number_id=phone_number_id,
                status="sending"
            )
            session.add(assistant_message)
            session.commit()
            message_id = assistant_message.id
        
        # Enviar respuesta a través de WhatsApp
        # Como send_message es async, necesitamos ejecutarlo en un event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                send_message(phone_number_id, wa_id, answer)
            )
            
            # Actualizar estado del mensaje
            with get_sync_session() as session:
                message = session.get(Message, message_id)
                if message:
                    message.status = "sent"
                    session.add(message)
                    session.commit()
                    
        finally:
            loop.close()
        
        # Actualizar última actividad del thread
        with get_sync_session() as session:
            thread = session.get(Thread, thread.id)
            if thread:
                thread.last_message_at = datetime.utcnow()
                session.add(thread)
                session.commit()
        
        return {
            "status": "success",
            "wa_id": wa_id,
            "response_sent": True
        }
        
    except Exception as e:
        # Reintentar en caso de error
        try:
            # Exponential backoff automático
            raise handle_message.retry(exc=e)
        except MaxRetriesExceededError:
            # Log del error después de todos los reintentos
            print(f"Error procesando mensaje después de {handle_message.max_retries} intentos: {str(e)}")
            return {
                "status": "failed",
                "wa_id": wa_id,
                "error": str(e)
            } 