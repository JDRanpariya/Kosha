# backend/scripts/run_ingestion.py

import logging
from sqlalchemy.orm import Session

from backend.db.database import SessionLocal
from backend.db.models import Source
from backend.services.ingestion import process_source
from backend.core.config import settings  # secrets now come from here

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Derived from registry — single source of truth

CATEGORY_MAP = {
    "rss": "newsletters",
    "arxiv": "papers",
    "spotify": "podcasts",   # ✅ fixed
    "youtube": "videos",
}

def sync_all():
    db: Session = SessionLocal()
    try:
        logger.info("Starting global ingestion sync...")
        sources = db.query(Source).filter(Source.enabled == True).all()
        logger.info(f"Found {len(sources)} enabled sources.")

        for source in sources:
            import copy
            config = copy.deepcopy(source.config_json)

            # Inject secrets from settings (already loaded from Docker secrets)
            if source.type == "spotify":
                config["client_id"] = settings.SPOTIFY_CLIENT_ID
                config["client_secret"] = settings.SPOTIFY_CLIENT_SECRET
            elif source.type == "youtube":
                config["api_key"] = settings.YOUTUBE_API_KEY

            # Temporarily swap config for injection
            original_config = source.config_json
            source.config_json = config

            category = CATEGORY_MAP.get(source.type)
            if category:
                new_count = process_source(db, source, category)
                print(f"✅ {source.name}: Added {new_count} new items.")
            else:
                logger.error(f"Unknown source type: {source.type}")

            source.config_json = original_config

    except Exception as e:
        logger.error(f"Error during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_all()
