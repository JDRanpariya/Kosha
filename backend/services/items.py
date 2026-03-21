# backend/services/items.py

"""
Item service - handles item CRUD operations.
"""

import hashlib
from datetime import datetime, timezone, timedelta
from typing import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exists

from backend.api.schemas.items import ItemSummary, ItemDetail
from backend.core.logging import get_logger
from backend.db.models import Item, ItemContent

logger = get_logger(__name__)


class ItemService:
    """Service for item-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, item_id: int) -> Item | None:
        """Get item by ID."""
        return self.db.query(Item).filter(Item.id == item_id).first()
    
    def get_by_content_hash(self, content_hash: str) -> Item | None:
        """Get item by content hash (for deduplication)."""
        return self.db.query(Item).filter(Item.content_hash == content_hash).first()
    
    def exists_by_hash(self, content_hash: str) -> bool:
        return self.db.query(
            exists().where(Item.content_hash == content_hash)
        ).scalar()
    
    def get_with_content(self, item_id: int) -> tuple[Item, ItemContent | None] | None:
        """Get item with its content."""
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        content = (
            self.db.query(ItemContent)
            .filter(ItemContent.item_id == item_id)
            .first()
        )
        
        return item, content
    
    def get_recent(self, hours: int = 24, limit: int = 20, offset: int = 0):
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        total = (
            self.db.query(func.count(Item.id))
            .filter(Item.published_at >= cutoff)
            .scalar()
        )
        items = (
            self.db.query(Item)
            .options(joinedload(Item.source))   # ← ADD THIS
            .filter(Item.published_at >= cutoff)
            .order_by(Item.published_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def get_by_ids(self, item_ids: list[int]) -> list[Item]:
        if not item_ids:
            return []
        return (
            self.db.query(Item)
            .options(joinedload(Item.source))   # ← ADD THIS
            .filter(Item.id.in_(item_ids))
            .all()
        )
    
    @staticmethod
    def compute_content_hash(url: str) -> str:
        """Compute content hash from URL."""
        return hashlib.sha256(url.encode()).hexdigest()
    
    @staticmethod
    def to_summary(item: Item, preview: str | None = None, similarity: float | None = None) -> ItemSummary:
        """Convert Item model to ItemSummary schema."""
        return ItemSummary(
            id=item.id,
            title=item.title,
            author=item.author,
            url=item.url,
            published_at=item.published_at,
            source_id=item.source_id,
            source_type=item.source.type if item.source else None,
            preview=preview,
            similarity=similarity,
        )
    
    @staticmethod
    def to_detail(item: Item, content: ItemContent | None = None) -> ItemDetail:
        """Convert Item model to ItemDetail schema."""
        return ItemDetail(
            id=item.id,
            title=item.title,
            author=item.author,
            url=item.url,
            published_at=item.published_at,
            source_id=item.source_id,
            content=content.parsed_content if content else None,
            metadata=content.metadata_json if content else {},
        )
