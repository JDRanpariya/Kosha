# backend/api/schemas/digest.py

"""
Digest endpoint schemas.
"""

from datetime import date

from backend.api.schemas.common import BaseSchema, PaginatedResponse
from backend.api.schemas.items import ItemSummary, ItemDetail


class DigestResponse(PaginatedResponse):
    """Daily/weekly digest response."""
    date: date
    items: list[ItemSummary]


class ItemDetailResponse(BaseSchema):
    """Single item detail response."""
    item: ItemDetail
