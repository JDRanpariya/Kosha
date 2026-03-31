# backend/services/ingestion.py

import copy
import hashlib
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from backend.db.models import Item, ItemContent, Source
from connectors.registry import CONNECTOR_REGISTRY, get_connector_class
from schemas.connector_output import ConnectorOutput

from backend.services.embedding import get_embedding_service


logger = logging.getLogger(__name__)


def _inject_secrets(source_type: str, config: dict) -> dict:
    from backend.core.config import settings
    config = copy.deepcopy(config)

    if source_type == "youtube":
        if not config.get("api_key"):
            config["api_key"] = settings.YOUTUBE_API_KEY
    elif source_type == "email_imap":
        if not config.get("username"):
            config["username"] = settings.EMAIL_USERNAME
        if not config.get("password"):
            config["password"] = settings.EMAIL_PASSWORD

    return config


def process_source(db: Session, source: Source, category: str) -> int:
    """Full ingestion workflow for a single source. Returns count of new items."""
    logger.info(f"Starting ingestion — source {
                source.id} type={source.type!r}")

    ConnectorClass = get_connector_class(category, source.type)
    if not ConnectorClass:
        logger.error(
            f"No connector registered for category={
                category!r} type={source.type!r}"
        )
        return 0

    config = _inject_secrets(source.type, source.config_json or {})

    try:
        connector = ConnectorClass(config)
    except Exception as exc:
        logger.error(f"Failed to initialise connector for source {
                     source.id}: {exc}")
        return 0

    try:
        fetched_items: list[ConnectorOutput] = connector.fetch()
    except Exception as exc:
        logger.error(
            f"Error fetching from source {source.id}: {exc}", exc_info=True
        )
        return 0

    new_items_count = 0

    embedding_service = get_embedding_service()

    for item in fetched_items:
        content_hash = hashlib.sha256(str(item.url).encode()).hexdigest()

        if db.query(Item).filter(Item.content_hash == content_hash).first():
            logger.debug(f"Duplicate skipped: {item.title!r}")
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

                if embedding_service.available and item.content:
                    db_content.embedding = embedding_service.encode(
                        item.content)

            new_items_count += 1

        except IntegrityError:
            logger.warning(f"Race-condition duplicate skipped: {item.title!r}")
        except Exception as exc:
            logger.error(f"Failed to save {item.title!r}: {
                         exc}", exc_info=True)

    source.last_fetched_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(
        f"Ingestion complete — source {source.id} added {
            new_items_count} new items."
    )
    return new_items_count


def run_ingestion_cycle(db: Session) -> None:
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
