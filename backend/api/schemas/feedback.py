# backend/api/schemas/feedback.py

"""
Feedback endpoint schemas.
"""

from typing import Literal

from backend.api.schemas.common import BaseSchema
from backend.api.schemas.items import ItemSummary


InteractionType = Literal["viewed", "saved", "dismissed"]


class FeedbackRequest(BaseSchema):
    """Feedback submission request."""
    item_id: int
    type: InteractionType


class FeedbackResponse(BaseSchema):
    """Feedback submission response."""
    status: str
    type: InteractionType
    item_id: int


class SavedItemsResponse(BaseSchema):
    """Saved items response."""
    count: int
    item_ids: list[int]
    items: list[ItemSummary]
