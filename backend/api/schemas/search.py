# backend/api/schemas/search.py

"""
Search endpoint schemas.
"""

from backend.api.schemas.common import BaseSchema
from backend.api.schemas.items import ItemSummary


class SearchRequest(BaseSchema):
    """Search query parameters."""
    q: str
    limit: int = 20


class SearchResponse(BaseSchema):
    """Search results response."""
    query: str
    count: int
    items: list[ItemSummary]


class SearchUnavailableResponse(BaseSchema):
    """Response when search is not available."""
    error: str
    available: bool = False
