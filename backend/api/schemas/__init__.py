# backend/api/schemas/__init__.py

"""
API schemas package.
"""

from backend.api.schemas.common import BaseSchema, StatusResponse, PaginatedResponse
from backend.api.schemas.items import ItemSummary, ItemDetail, ItemCreate
from backend.api.schemas.digest import DigestResponse, ItemDetailResponse
from backend.api.schemas.search import SearchRequest, SearchResponse, SearchUnavailableResponse
from backend.api.schemas.sources import (
    SourceType,
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceListResponse,
    SourceCreatedResponse,
)
from backend.api.schemas.feedback import (
    InteractionType,
    FeedbackRequest,
    FeedbackResponse,
    SavedItemsResponse,
)

__all__ = [
    # Common
    "BaseSchema",
    "StatusResponse", 
    "PaginatedResponse",
    # Items
    "ItemSummary",
    "ItemDetail",
    "ItemCreate",
    # Digest
    "DigestResponse",
    "ItemDetailResponse",
    # Search
    "SearchRequest",
    "SearchResponse",
    "SearchUnavailableResponse",
    # Sources
    "SourceType",
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    "SourceListResponse",
    "SourceCreatedResponse",
    # Feedback
    "InteractionType",
    "FeedbackRequest",
    "FeedbackResponse",
    "SavedItemsResponse",
]
