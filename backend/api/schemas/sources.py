# backend/api/schemas/sources.py

"""
Source management schemas.
"""

from datetime import datetime
from typing import Any, Literal

from backend.api.schemas.common import BaseSchema, StatusResponse


SourceType = Literal[
    "rss", "substack", "email_imap",     # newsletters
    "arxiv",                             # papers
    "hackernews", "reddit", "github",    # social / dev
    "spotify",                           # podcasts
    "youtube", "youtube_subscriptions",  # videos
]


class SourceBase(BaseSchema):
    """Base source fields."""
    name: str
    type: SourceType
    url: str | None = None
    config_json: dict[str, Any] = {}


class SourceCreate(SourceBase):
    """Schema for creating a source."""
    pass


class SourceUpdate(BaseSchema):
    """Schema for updating a source."""
    name: str | None = None
    enabled: bool | None = None
    config_json: dict[str, Any] | None = None


class SourceResponse(SourceBase):
    """Full source response."""
    id: int
    enabled: bool
    last_fetched_at: datetime | None = None

    model_config = {"from_attributes": True}


class SourceListResponse(BaseSchema):
    """List of sources."""
    sources: list[SourceResponse]
    count: int


class SourceCreatedResponse(BaseSchema):
    """Response after creating a source."""
    id: int
    name: str
