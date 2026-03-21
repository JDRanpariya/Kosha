import copy
import hashlib
import logging

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from backend.db.models import Item, ItemContent, Source
from connectors.registry import CONNECTOR_REGISTRY
from schemas.connector_output import ConnectorOutput

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDINGS_ENABLED = True
except ImportError:
    EMBEDDINGS_ENABLED = False

logger = logging.getLogger(__name__)


def _inject_secrets(source_type: str, config: dict) -> dict:
    """
    Inject API credentials from settings into a config dict.
    Only fills in keys that are missing or empty so that explicit
    config values (e.g. in tests) are never overwritten.
    """
    from backend.core.config import settings

    config = copy.deepcopy(config)

    if source_type == "spotify":
        if not config.get("client_id"):
            config["client_id"] = settings.SPOTIFY_CLIENT_ID
        if not config.get("client_secret"):
            config["client_secret"] = settings.SPOTIFY_CLIENT_SECRET
    elif source_type == "youtube":
        if not config.get("api_key"):
            config["api_key"] = settings.YOUTUBE_API_KEY

    return config


def get_connector_class(category: str, source_type: str):
    try:
        return CONNECTOR_REGISTRY[category][source_type]["class"]
    except KeyError:
        logger.error(
            f"No connector found for category '{category}' and type '{source_type}'"
        )
        return None


def process_source(db: Session, source: Source, category: str) -> int:
    """Full ingestion workflow for a single source."""
    logger.info(f"Starting ingestion for source {source.id} ({source.type})")

    ConnectorClass = get_connector_class(category, source.type)
    if not ConnectorClass:
        return 0

    config = _inject_secrets(source.type, source.config_json or {})

    try:
        connector = ConnectorClass(config)
    except Exception as e:
        logger.error(f"Failed to initialise connector for source {source.id}: {e}")
        return 0

    try:
        fetched_items: list[ConnectorOutput] = connector.fetch()
    except Exception as e:
        logger.error(f"Error fetching from source {source.id}: {e}")
        return 0

    new_items_count = 0

    for item in fetched_items:
        content_hash = hashlib.sha256(str(item.url).encode()).hexdigest()

        if db.query(Item).filter(Item.content_hash == content_hash).first():
            logger.debug(f"Skipping existing item: {item.title}")
            continue

        try:
            with db.begin_nested():
                db_item = Item(
                    source_id=source.id,
                    external_id=str(item.url),
                    title=item.title,
                    author=item.author,
                    published_at=item.published_at,
                    url=str(item.url),
                    content_hash=content_hash,
                )
                db.add(db_item)
                db.flush()

                db_content = ItemContent(
                    item_id=db_item.id,
                    raw_content=item.content,
                    parsed_content=item.content,
                    metadata_json=item.metadata,
                )
                db.add(db_content)

                if EMBEDDINGS_ENABLED and item.content:
                    # Let the model handle truncation internally — do NOT
                    # slice by characters ([:512] cuts tokens unpredictably).
                    embedding = _model.encode(
                        item.content,
                        show_progress_bar=False,
                    ).tolist()
                    db_content.embedding = embedding

            new_items_count += 1

        except IntegrityError:
            logger.warning(f"Race-condition duplicate skipped: {item.title}")
        except Exception as e:
            logger.error(f"Failed to save '{item.title}': {e}", exc_info=True)

    source.last_fetched_at = func.now()
    db.commit()

    logger.info(
        f"Ingestion complete for source {source.id}. Added {new_items_count} new items."
    )
    return new_items_count


def run_ingestion_cycle(db: Session):
    """Orchestrator called by the Celery worker."""
    for category, types in CONNECTOR_REGISTRY.items():
        for source_type in types:
            sources = (
                db.query(Source)
                .filter(Source.type == source_type, Source.enabled == True)
                .all()
            )
            for source in sources:
                process_source(db, source, category)
