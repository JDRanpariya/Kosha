"""All API schemas in one place."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, HttpUrl


# ── Base ──────────────────────────────────────────────────────────────────

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class StatusResponse(BaseSchema):
    status: str
    message: str | None = None

class PaginatedResponse(BaseSchema):
    total: int
    limit: int
    offset: int


# ── Items ─────────────────────────────────────────────────────────────────

class ItemSummary(BaseSchema):
    id: int
    title: str
    author: str | None = None
    url: str
    published_at: datetime | None = None
    source_id: int
    source_type: str | None = None
    preview: str | None = None
    similarity: float | None = None

class ItemDetail(ItemSummary):
    content: str | None = None
    metadata: dict[str, Any] = {}

class ItemCreate(BaseSchema):
    source_id: int
    external_id: str
    title: str
    author: str | None = None
    url: HttpUrl
    published_at: datetime | None = None
    content: str | None = None
    metadata: dict[str, Any] = {}


# ── Digest ────────────────────────────────────────────────────────────────

class DigestResponse(PaginatedResponse):
    date: date
    items: list[ItemSummary]

class ItemDetailResponse(BaseSchema):
    item: ItemDetail


# ── Search ────────────────────────────────────────────────────────────────

class SearchResponse(BaseSchema):
    query: str
    count: int
    items: list[ItemSummary]

class SearchUnavailableResponse(BaseSchema):
    error: str
    available: bool = False


# ── Sources ───────────────────────────────────────────────────────────────

SourceType = Literal[
    "rss", "substack", "email_imap",
    "arxiv",
    "hackernews", "reddit",
    "youtube",
]

class SourceCreate(BaseSchema):
    name: str
    type: SourceType
    url: str | None = None
    config_json: dict[str, Any] = {}

class SourceUpdate(BaseSchema):
    name: str | None = None
    enabled: bool | None = None
    config_json: dict[str, Any] | None = None

class SourceResponse(BaseSchema):
    id: int
    name: str
    type: str
    url: str | None = None
    config_json: dict[str, Any] = {}
    enabled: bool
    last_fetched_at: datetime | None = None

class SourceListResponse(BaseSchema):
    sources: list[SourceResponse]
    count: int

class SourceCreatedResponse(BaseSchema):
    id: int
    name: str


# ── Feedback ──────────────────────────────────────────────────────────────

InteractionType = Literal["viewed", "saved", "dismissed", "unsave"]

class FeedbackRequest(BaseSchema):
    item_id: int
    type: InteractionType

class FeedbackResponse(BaseSchema):
    status: str
    type: InteractionType
    item_id: int

class SavedItemsResponse(BaseSchema):
    count: int
    item_ids: list[int]
    items: list[ItemSummary]
