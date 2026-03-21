from backend.worker.celery_app import celery_app
from backend.db.database import SessionLocal
from backend.services.ingestion import run_ingestion_cycle
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def run_ingestion():
    db = SessionLocal()
    try:
        logger.info("Running scheduled ingestion cycle...")
        run_ingestion_cycle(db)
    finally:
        db.close()
