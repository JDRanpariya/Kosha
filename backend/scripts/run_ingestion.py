import logging
from sqlalchemy.orm import Session

from backend.db.database import SessionLocal
from backend.services.ingestion import run_ingestion_cycle

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def sync_all():
    db: Session = SessionLocal()
    try:
        logger.info("Starting global ingestion sync...")
        run_ingestion_cycle(db)
        logger.info("Sync complete.")
    except Exception as e:
        logger.error(f"Error during sync: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    sync_all()
