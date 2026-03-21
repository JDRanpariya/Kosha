# backend/api/schemas/feedback.py

from typing import Literal
from backend.api.schemas.common import BaseSchema
from backend.api.schemas.items import ItemSummary

# Added 'unsave' — the frontend sends this to remove a saved interaction.

# 'viewed' is kept for future implicit tracking (e.g. scroll-past).

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
