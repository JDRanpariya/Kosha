import hashlib
import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from backend.db.models import Item, ItemContent, Source
from connectors.registry import CONNECTOR_REGISTRY
from schemas.connector_output import ConnectorOutput

from sqlalchemy.exc import IntegrityError

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dims, matches your column
    EMBEDDINGS_ENABLED = True
except ImportError:
    EMBEDDINGS_ENABLED = False

logger = logging.getLogger(__name__)

def get_connector_class(category: str, source_type: str):
    """
    Dynamically look up the connector class from the registry.
    """
    try:
        return CONNECTOR_REGISTRY[category][source_type]["class"]
    except KeyError:
        logger.error(f"No connector found for category '{category}' and type '{source_type}'")
        return None

def process_source(db: Session, source: Source, category: str):
    """
    Full ingestion workflow for a single source.
    """
    logger.info(f"Starting ingestion for source {source.id} ({source.type})")

    ConnectorClass = get_connector_class(category, source.type)
    if not ConnectorClass:
        return 0

    try:
        connector = ConnectorClass(source.config_json)
    except Exception as e:
        logger.error(f"Failed to initialize connector for source {source.id}: {e}")
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

                # ✅ Assign to variable so we can set embedding on it
                db_item_content = ItemContent(
                    item_id=db_item.id,
                    raw_content=item.content,
                    parsed_content=item.content,
                    metadata_json=item.metadata,
                )
                db.add(db_item_content)

                if EMBEDDINGS_ENABLED and item.content:
                    embedding = _model.encode(item.content[:512]).tolist()
                    db_item_content.embedding = embedding  # ✅ correct reference

            new_items_count += 1

        except IntegrityError:
            logger.warning(f"Race condition duplicate for: {item.title}")
        except Exception as e:
            logger.error(f"Failed to save '{item.title}': {e}", exc_info=True)  # ✅ exc_info shows full traceback

    source.last_fetched_at = func.now()
    db.commit()

    logger.info(f"Ingestion complete. Added {new_items_count} new items for source {source.id}.")
    return new_items_count

def run_ingestion_cycle(db: Session):
    """
    Orchestrator to run through all enabled sources.
    """
    # Iterate through each category and type in your registry
    for category, types in CONNECTOR_REGISTRY.items():
        for source_type in types:
            # Find all enabled sources of this type in the database
            sources = db.query(Source).filter(
                Source.type == source_type, 
                Source.enabled == True
            ).all()
            
            for source in sources:
                process_source(db, source, category)
