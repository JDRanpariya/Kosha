# backend/api/routes/feedback.py

from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> FeedbackResponse:
    """Submit user feedback for an item."""
    # Verify item exists
    if not db.query(Item).filter(Item.id == payload.item_id).first():
        raise HTTPException(status_code=404, detail="Item not found")
    
    interaction = Interaction(
        user_id=user_id,
        item_id=payload.item_id,
        type=payload.type,
    )
    db.add(interaction)
    db.commit()
    
    return FeedbackResponse(
        status="ok",
        type=payload.type,
        item_id=payload.item_id,
    )


@router.get("/saved", response_model=SavedItemsResponse)
def get_saved_items(
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> SavedItemsResponse:
    """Get all items saved by the user."""
    saved_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == user_id, Interaction.type == "saved")
        .all()
    )
    
    item_ids = [i.item_id for i in saved_interactions]
    service = ItemService(db)
    items = service.get_by_ids(item_ids)
    
    return SavedItemsResponse(
        count=len(item_ids),
        item_ids=item_ids,
        items=[ItemService.to_summary(item) for item in items],
    )
