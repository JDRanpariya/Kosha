from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings

celery_app = Celery(
    "kosha",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["backend.worker.tasks"]
)

celery_app.conf.beat_schedule = {
    "run-ingestion-every-6-hours": {
        "task": "backend.worker.tasks.run_ingestion",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}
celery_app.conf.timezone = "UTC"
