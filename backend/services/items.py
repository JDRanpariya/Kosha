# backend/services/items.py

import hashlib
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, exists
from sqlalchemy.orm import Session, joinedload

from backend.api.schemas.items import ItemSummary, ItemDetail
from backend.core.logging import get_logger
from backend.db.models import Item, ItemContent, Interaction, Source

logger = get_logger(__name__)


class ItemService:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int) -> Item | None:
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_by_content_hash(self, content_hash: str) -> Item | None:
        return self.db.query(Item).filter(Item.content_hash == content_hash).first()

    def exists_by_hash(self, content_hash: str) -> bool:
        return self.db.query(
            exists().where(Item.content_hash == content_hash)
        ).scalar()

    def get_with_content(self, item_id: int) -> tuple[Item, ItemContent | None] | None:
        item = self.get_by_id(item_id)
        if not item:
            return None
        content = (
            self.db.query(ItemContent)
            .filter(ItemContent.item_id == item_id)
            .first()
        )
        return item, content

    def get_recent(
        self,
        user_id: int,
        hours: int = 24,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Item], int]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        dismissed_sq = (
            self.db.query(Interaction.item_id)
            .filter(
                Interaction.user_id == user_id,
                Interaction.type == "dismissed",
            )
            .subquery()
        )

        # ── FIX: scope to this user's sources ──────────────────────
        user_source_ids = (
            self.db.query(Source.id)
            .filter(Source.user_id == user_id)
            .subquery()
        )

        base_filter = [
            Item.published_at >= cutoff,
            Item.source_id.in_(user_source_ids),   # ← ADD THIS
            ~Item.id.in_(dismissed_sq),
        ]
        # ───────────────────────────────────────────────────────────

        total = (
            self.db.query(func.count(Item.id))
            .filter(*base_filter)
            .scalar()
        )

        items = (
            self.db.query(Item)
            .options(joinedload(Item.source))
            .filter(*base_filter)
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
            .options(joinedload(Item.source))
            .filter(Item.id.in_(item_ids))
            .all()
        )

    @staticmethod
    def compute_content_hash(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    @staticmethod
    def to_summary(
        item: Item,
        preview: str | None = None,
        similarity: float | None = None,
    ) -> ItemSummary:
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
        return ItemDetail(
            id=item.id,
            title=item.title,
            author=item.author,
            url=item.url,
            published_at=item.published_at,
            source_id=item.source_id,
            source_type=item.source.type if item.source else None,
            content=content.parsed_content if content else None,
            metadata=content.metadata_json if content else {},
        )
