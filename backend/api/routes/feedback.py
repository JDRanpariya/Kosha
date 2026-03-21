# backend/api/routes/feedback.py
# Added: POST /feedback/teach — records teach signals for Phase 2 preference learning.
# The existing save/dismiss endpoints are unchanged.

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, ensure_user_exists
from backend.api.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    SavedItemsResponse,
    ItemSummary,
)
from backend.db.models import Interaction, Item
from backend.services.items import ItemService

router = APIRouter()


# ── Existing endpoints (unchanged) ────────────────────────────────────────

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> FeedbackResponse:
    """Submit save / dismiss feedback for an item."""
    if not db.query(Item).filter(Item.id == payload.item_id).first():
        raise HTTPException(status_code=404, detail="Item not found")

    interaction = Interaction(
        user_id=user_id,
        item_id=payload.item_id,
        type=payload.type,
    )
    db.add(interaction)
    db.commit()

    return FeedbackResponse(status="ok", type=payload.type, item_id=payload.item_id)


@router.get("/saved", response_model=SavedItemsResponse)
def get_saved_items(
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> SavedItemsResponse:
    """Return all items the user has saved to their reading list."""
    saved = (
        db.query(Interaction)
        .filter(Interaction.user_id == user_id, Interaction.type == "saved")
        .all()
    )
    item_ids = [i.item_id for i in saved]
    service = ItemService(db)
    items = service.get_by_ids(item_ids)

    return SavedItemsResponse(
        count=len(item_ids),
        item_ids=item_ids,
        items=[ItemService.to_summary(item) for item in items],
    )


# ── Phase 2 seed endpoint ─────────────────────────────────────────────────

class TeachSignalRequest(BaseModel):
    """
    Records WHY the user found an item interesting.

    This is the primary training signal for the Phase 2 preference model.
    Unlike thumbs-up/down, it captures the user's reasoning — not just polarity.

    selected_tags: list of reason tags the user clicked (e.g. "Challenges my assumptions")
    note: optional free-text elaboration (Phase 2+ UI)
    """
    item_id: int
    selected_tags: list[str]
    note: str | None = None


@router.post("/teach")
def submit_teach_signal(
    payload: TeachSignalRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> dict:
    """
    Store a teach signal — why the user found this item interesting.

    Stored as an Interaction with type='teach' and the tags in metadata_json.
    The intelligence layer will consume these in Phase 2.
    """
    if not db.query(Item).filter(Item.id == payload.item_id).first():
        raise HTTPException(status_code=404, detail="Item not found")

    interaction = Interaction(
        user_id=user_id,
        item_id=payload.item_id,
        type="teach",
        metadata_json={
            "selected_tags": payload.selected_tags,
            "note": payload.note,
        },
    )
    db.add(interaction)
    db.commit()

    return {"status": "ok", "tags_recorded": len(payload.selected_tags)}
