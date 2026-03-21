import hashlib
import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from backend.db.models import Item, ItemContent, Source
from connectors.registry import CONNECTOR_REGISTRY
from schemas.connector_output import ConnectorOutput

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
    
    # 1. Dynamically get the connector class from your registry
    ConnectorClass = get_connector_class(category, source.type)
    if not ConnectorClass:
        return 0

    # 2. Instantiate with source-specific config
    try:
        connector = ConnectorClass(source.config_json)
    except Exception as e:
        logger.error(f"Failed to initialize connector for source {source.id}: {e}")
        return 0

    # 3. Fetch items using the connector's standardized output
    try:
        fetched_items: list[ConnectorOutput] = connector.fetch()
    except Exception as e:
        logger.error(f"Error fetching from source {source.id}: {e}")
        return 0

    new_items_count = 0
    for item in fetched_items:
        # 4. Deduplication: Generate a unique content hash
        # We use the URL as a stable identifier for now.
        url_hash = hashlib.sha256(str(item.url).encode()).hexdigest()
        
        # Check if the item already exists in the database
        existing_item = db.query(Item).filter(Item.content_hash == url_hash).first()
        if existing_item:
            logger.debug(f"Skipping existing item: {item.title}")
            continue
            
        # 5. Atomic Storage: Save metadata and content
        try:
            # Create core metadata record
            db_item = Item(
                source_id=source.id,
                external_id=str(item.url),
                title=item.title,
                author=item.author,
                published_at=item.published_at,
                url=str(item.url),
                content_hash=content_hash
            )
            db.add(db_item)
            db.flush() # Flush to get the ID for the content record
            
            # Create associated content record
            db_content = ItemContent(
                item_id=db_item.id,
                raw_content=item.content,
                parsed_content=item.content, # Normalized markdown
                metadata_json=item.metadata
            )
            db.add(db_content)
            new_items_count += 1
            
        except Exception as e:
            logger.error(f"Failed to save item {item.title}: {e}")
            db.rollback()
            continue

    # 6. Finalize: Update source status and commit
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
