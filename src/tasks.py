from celery import Celery
from src.core.settings import settings

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
    accept_content=['json']
)

@celery_app.task
def handle_message(message: dict):
    # Tu lógica de manejo de mensajes aquí
    return {"status": "processed", "message": message}