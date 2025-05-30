from celery import Celery
from src.core.settings import settings

celery_app = Celery(
    "whatsapp_bot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.tasks.message_handler",
        "src.tasks.conversation_monitor"
    ]
)

celery_app.conf.beat_schedule = {
    "check-inactive-conversations": {
        "task": "src.tasks.conversation_monitor.check_inactive_conversations",
        "schedule": 60.0,
    }
} 