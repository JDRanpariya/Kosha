# backend/services/ingestion.py

"""
Ingestion service - orchestrates content fetching, storage, and embedding.
Cleanly separated into distinct responsibilities.
"""

import copy
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from backend.core.constants import CATEGORY_MAP
from backend.core.logging import get_logger, set_correlation_id
from backend.db.models import Item, ItemContent, Source
from backend.services.embedding import get_embedding_service
from backend.services.items import ItemService
from connectors.registry import CONNECTOR_REGISTRY
from schemas.connector_output import ConnectorOutput

logger = get_logger(__name__)


class IngestionService:
    """
    Service for ingesting content from sources.
    
    Separates concerns:
    - Connector management (instantiation, credential injection)
    - Content fetching (calling connector.fetch())
    - Persistence (storing items and content)
    - Embedding generation (via EmbeddingService)

    """
    
    def __init__(self, db: Session):
        self.db = db
        self.item_service = ItemService(db)
        self.embedding_service = get_embedding_service()
    
    def process_source(self, source: Source) -> int:
        """
        Full ingestion workflow for a single source.
        
        Args:
            source: Source model instance
            
        Returns:
            Number of new items added
        """
        correlation_id = set_correlation_id()
        logger.info(
            f"Starting ingestion for source",
            extra={
                "source_id": source.id,
                "source_type": source.type,
                "source_name": source.name,
            }
        )
        
        # 1. Resolve category and connector
        category = CATEGORY_MAP.get(source.type)
        if not category:
            logger.warning(f"Unknown source type: {source.type}")
            return 0
        
        connector = self._create_connector(source, category)
        if not connector:
            return 0
        
        # 2. Fetch content
        fetched_items = self._fetch_items(connector, source.id)
        if not fetched_items:
            return 0
        
        # 3. Store items
        new_count = self._store_items(source, fetched_items)
        
        # 4. Update source timestamp
        source.last_fetched_at = func.now()
        self.db.commit()
        
        logger.info(
            f"Ingestion complete",
            extra={
                "source_id": source.id,
                "fetched": len(fetched_items),
                "new_items": new_count,
            }
        )
        
        return new_count
    
    def _create_connector(self, source: Source, category: str):
        """Create and configure connector instance."""
        ConnectorClass = self._get_connector_class(category, source.type)
        if not ConnectorClass:
            return None
        
        config = self._inject_secrets(source.type, source.config_json or {})
        
        try:
            return ConnectorClass(config)
        except Exception as e:
            logger.error(
                f"Failed to initialize connector",
                extra={"source_id": source.id, "error": str(e)},
            )
            return None
    
    def _get_connector_class(self, category: str, source_type: str):
        """Look up connector class from registry."""
        try:
            return CONNECTOR_REGISTRY[category][source_type]["class"]
        except KeyError:
            logger.error(
                f"No connector found",
                extra={"category": category, "source_type": source_type},
            )
            return None
    
    def _inject_secrets(self, source_type: str, config: dict) -> dict:
        """Inject API credentials from settings into config dict."""
        from backend.core.config import settings
        
        config = copy.deepcopy(config)
        
        if source_type == "spotify":
            config.setdefault("client_id", settings.SPOTIFY_CLIENT_ID)
            config.setdefault("client_secret", settings.SPOTIFY_CLIENT_SECRET)
        elif source_type == "youtube":
            config.setdefault("api_key", settings.YOUTUBE_API_KEY)
        
        return config
    
    def _fetch_items(
        self,
        connector,
        source_id: int,
    ) -> list[ConnectorOutput]:
        """Fetch items from connector."""
        try:
            items = connector.fetch()
            logger.debug(f"Fetched {len(items)} items from source {source_id}")
            return items
        except Exception as e:
            logger.error(
                f"Error fetching from source",
                extra={"source_id": source_id, "error": str(e)},
                exc_info=True,
            )
            return []
    
    def _store_items(
        self,
        source: Source,
        items: list[ConnectorOutput],
    ) -> int:
        """Store items and their content, with embedding generation."""
        new_count = 0
        
        for item in items:
            content_hash = ItemService.compute_content_hash(str(item.url))
            
            # Skip duplicates
            if self.item_service.exists_by_hash(content_hash):
                logger.debug(f"Skipping duplicate: {item.title[:50]}")
                continue
            
            try:
                new_count += self._store_single_item(source, item, content_hash)
            except IntegrityError:
                self.db.rollback()
                logger.warning(f"Race-condition duplicate: {item.title[:50]}")
            except Exception as e:
                self.db.rollback()
                logger.error(
                    f"Failed to save item",
                    extra={"title": item.title[:50], "error": str(e)},
                    exc_info=True,
                )
        
        return new_count
    
    def _store_single_item(
        self,
        source: Source,
        item: ConnectorOutput,
        content_hash: str,
    ) -> int:
        """Store a single item with its content and embedding."""
        with self.db.begin_nested():
            # Create item
            db_item = Item(
                source_id=source.id,
                external_id=str(item.url),
                title=item.title,
                author=item.author,
                published_at=item.published_at,
                url=str(item.url),
                content_hash=content_hash,
            )
            self.db.add(db_item)
            self.db.flush()
            
            # Create content
            db_content = ItemContent(
                item_id=db_item.id,
                raw_content=item.content,
                parsed_content=item.content,
                metadata_json=item.metadata,
            )
            
            # Generate embedding
            if item.content:
                embedding = self.embedding_service.encode(item.content)
                if embedding:
                    db_content.embedding = embedding
            
            self.db.add(db_content)
        
        return 1


def process_source(db: Session, source: Source, category: str) -> int:
    """
    Legacy function for backward compatibility.
    Wraps IngestionService.process_source().
    """
    service = IngestionService(db)
    return service.process_source(source)


def run_ingestion_cycle(db: Session) -> None:
    """
    Run ingestion for all enabled sources.
    Called by Celery worker.
    """
    service = IngestionService(db)
    
    for category, types in CONNECTOR_REGISTRY.items():
        for source_type in types:
            sources = (
                db.query(Source)
                .filter(Source.type == source_type, Source.enabled == True)
                .all()
            )
            for source in sources:
                service.process_source(source)
