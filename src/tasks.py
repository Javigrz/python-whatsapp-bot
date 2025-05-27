from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from src.core.settings import settings
from src.core.openai_client import get_answer
from src.core.meta_client import send_message
import asyncio
import time

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
        # Obtener respuesta de OpenAI
        answer = get_answer(agent_id, text)
        
        # Enviar respuesta a través de WhatsApp
        # Como send_message es async, necesitamos ejecutarlo en un event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                send_message(phone_number_id, wa_id, answer)
            )
        finally:
            loop.close()
        
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