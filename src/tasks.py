from celery import Celery
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.settings import settings
from src.core.database import get_database_manager
from src.core.models import Thread, Client, Agent
from src.core.openai_client import get_openai_client, OpenAIError
from src.core.meta_client import MetaClient, MetaError
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    'src.tasks',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configuración de Celery
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True
)


@celery_app.task(bind=True, max_retries=3)
def handle_message(self, agent_id: str, phone_number_id: str, wa_id: str, text: str):
    """
    Procesa un mensaje de WhatsApp y genera una respuesta usando OpenAI.
    
    Args:
        agent_id: ID del assistant de OpenAI
        phone_number_id: ID del número de WhatsApp Business
        wa_id: ID de WhatsApp del usuario
        text: Texto del mensaje recibido
    """
    try:
        logger.info(f"🤖 Procesando mensaje de {wa_id}: {text}")
        
        # Ejecutar la lógica asíncrona en un loop de evento
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                _process_message_async(agent_id, phone_number_id, wa_id, text)
            )
            logger.info(f"✅ Mensaje procesado exitosamente para {wa_id}")
            return response
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {str(e)}")
        # Reintentar hasta 3 veces
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Reintentando... ({self.request.retries + 1}/{self.max_retries})")
            raise self.retry(countdown=60, exc=e)
        else:
            logger.error(f"💀 Falló después de {self.max_retries} intentos")
            return {"status": "failed", "error": str(e)}


async def _process_message_async(agent_id: str, phone_number_id: str, wa_id: str, text: str):
    """
    Lógica asíncrona para procesar mensajes.
    """
    # Obtener managers
    db_manager = get_database_manager()
    openai_client = get_openai_client()
    meta_client = MetaClient()
    
    async with db_manager.get_session() as session:
        # 1. Buscar o crear thread para este usuario
        thread_id = await _get_or_create_thread(session, wa_id, agent_id, phone_number_id)
        
        if not thread_id:
            raise Exception("No se pudo obtener o crear thread")
        
        # 2. Añadir mensaje del usuario al thread de OpenAI
        try:
            openai_client._ensure_client()
            openai_client.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=text
            )
            
            # 3. Ejecutar el assistant
            run = openai_client.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=agent_id
            )
            
            # 4. Esperar respuesta
            import time
            while run.status in ["queued", "in_progress"]:
                time.sleep(0.5)
                run = openai_client.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # 5. Obtener la respuesta
                messages = openai_client.client.beta.threads.messages.list(
                    thread_id=thread_id,
                    limit=1
                )
                
                if messages.data:
                    response_text = messages.data[0].content[0].text.value
                    
                    # 6. Procesar texto para WhatsApp (limpiar formato)
                    response_text = _process_text_for_whatsapp(response_text)
                    
                    # 7. Enviar respuesta a WhatsApp
                    await meta_client.send_message(phone_number_id, wa_id, response_text)
                    
                    # 8. Actualizar timestamp del thread
                    await _update_thread_timestamp(session, wa_id, agent_id)
                    
                    logger.info(f"📤 Respuesta enviada a {wa_id}: {response_text[:50]}...")
                    
                    return {
                        "status": "success",
                        "response": response_text,
                        "thread_id": thread_id
                    }
                else:
                    raise Exception("No se obtuvo respuesta del assistant")
            else:
                raise Exception(f"Run falló con estado: {run.status}")
                
        except OpenAIError as e:
            logger.error(f"❌ Error OpenAI: {str(e)}")
            # Enviar mensaje de error genérico al usuario
            error_msg = "Disculpa, estoy experimentando dificultades técnicas. Por favor, intenta de nuevo en unos minutos."
            await meta_client.send_message(phone_number_id, wa_id, error_msg)
            raise e
        except MetaError as e:
            logger.error(f"❌ Error Meta: {str(e)}")
            raise e


async def _get_or_create_thread(session: AsyncSession, wa_id: str, agent_id: str, phone_number_id: str) -> str:
    """
    Busca un thread existente para el usuario o crea uno nuevo.
    """
    # Buscar thread existente por wa_id y assistant
    # Primero intentar buscar por cliente
    result = await session.execute(
        select(Thread, Client).join(Client).where(
            Thread.wa_id == wa_id,
            Client.assistant_id == agent_id,
            Client.phone_number_id == phone_number_id,
            Client.active == True
        )
    )
    row = result.first()
    
    if row:
        thread, client = row
        logger.info(f"📱 Thread existente encontrado para {wa_id}: {thread.thread_id}")
        return thread.thread_id
    
    # Si no se encuentra por cliente, buscar por agent (compatibilidad)
    result = await session.execute(
        select(Thread, Agent).join(Agent).where(
            Thread.wa_id == wa_id,
            Agent.agent_id == agent_id,
            Agent.phone_number_id == phone_number_id
        )
    )
    row = result.first()
    
    if row:
        thread, agent = row
        logger.info(f"📱 Thread existente encontrado para {wa_id}: {thread.thread_id}")
        return thread.thread_id
    
    # Crear nuevo thread
    try:
        openai_client = get_openai_client()
        openai_client._ensure_client()
        
        new_thread = openai_client.client.beta.threads.create()
        
        # Buscar el cliente o agent para asociar el thread
        client_result = await session.execute(
            select(Client).where(
                Client.assistant_id == agent_id,
                Client.phone_number_id == phone_number_id,
                Client.active == True
            )
        )
        client = client_result.scalar_one_or_none()
        
        if client:
            # Crear thread asociado al cliente
            db_thread = Thread(
                wa_id=wa_id,
                thread_id=new_thread.id,
                client_id=client.id
            )
        else:
            # Buscar agent para compatibilidad
            agent_result = await session.execute(
                select(Agent).where(
                    Agent.agent_id == agent_id,
                    Agent.phone_number_id == phone_number_id
                )
            )
            agent = agent_result.scalar_one_or_none()
            
            if agent:
                db_thread = Thread(
                    wa_id=wa_id,
                    thread_id=new_thread.id,
                    agent_id=agent.id
                )
            else:
                # Crear thread sin asociación (fallback)
                db_thread = Thread(
                    wa_id=wa_id,
                    thread_id=new_thread.id
                )
        
        session.add(db_thread)
        await session.commit()
        
        logger.info(f"🆕 Nuevo thread creado para {wa_id}: {new_thread.id}")
        return new_thread.id
        
    except Exception as e:
        logger.error(f"❌ Error creando thread: {str(e)}")
        raise e


async def _update_thread_timestamp(session: AsyncSession, wa_id: str, agent_id: str):
    """
    Actualiza el timestamp del último mensaje del thread.
    """
    try:
        from datetime import datetime
        
        # Buscar thread por cliente
        result = await session.execute(
            select(Thread).join(Client).where(
                Thread.wa_id == wa_id,
                Client.assistant_id == agent_id,
                Client.active == True
            )
        )
        thread = result.scalar_one_or_none()
        
        if not thread:
            # Buscar por agent (compatibilidad)
            result = await session.execute(
                select(Thread).join(Agent).where(
                    Thread.wa_id == wa_id,
                    Agent.agent_id == agent_id
                )
            )
            thread = result.scalar_one_or_none()
        
        if thread:
            thread.last_message_at = datetime.utcnow()
            await session.commit()
            
    except Exception as e:
        logger.error(f"❌ Error actualizando timestamp: {str(e)}")


def _process_text_for_whatsapp(text: str) -> str:
    """
    Procesa el texto de respuesta para que sea compatible con WhatsApp.
    """
    import re
    
    # Remover referencias de archivos/documentos
    text = re.sub(r"\【.*?\】", "", text).strip()
    
    # Convertir markdown bold (**texto**) a WhatsApp bold (*texto*)
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)
    
    # Limpiar espacios extra
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Limitar longitud (WhatsApp tiene límite de 4096 caracteres)
    if len(text) > 4000:
        text = text[:3980] + "\n\n..." + "\n\n(Mensaje truncado por longitud)"
    
    return text.strip()