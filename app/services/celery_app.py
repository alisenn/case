from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.services.queue"]
)

celery_app.conf.task_routes = {
    "app.services.queue.process_task": "main-queue"
}
