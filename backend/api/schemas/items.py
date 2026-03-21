# backend/api/schemas/items.py

"""
Item-related schemas.
"""

from datetime import datetime
from typing import Any

from pydantic import HttpUrl

from backend.api.schemas.common import BaseSchema


class ItemSummary(BaseSchema):
    """Item summary for list views."""
    id: int
    title: str
    author: str | None = None
    url: str
    published_at: datetime | None = None
    source_id: int
    preview: str | None = None
    similarity: float | None = None


class ItemDetail(ItemSummary):
    """Full item detail with content."""
    content: str | None = None
    metadata: dict[str, Any] = {}


class ItemCreate(BaseSchema):
    """Schema for creating items (internal use)."""
    source_id: int
    external_id: str
    title: str
    author: str | None = None
    url: HttpUrl
    published_at: datetime | None = None
    content: str | None = None
    metadata: dict[str, Any] = {}
