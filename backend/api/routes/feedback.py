from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Literal

from backend.db.database import get_db
from backend.db.models import Interaction, Item

router = APIRouter()

class FeedbackRequest(BaseModel):
    item_id: int
    type: Literal["viewed", "saved", "dismissed"]
    user_id: int = 1  # hardcoded until auth is added

@router.post("/")
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    if not db.query(Item).filter(Item.id == payload.item_id).first():
        raise HTTPException(status_code=404, detail="Item not found")

    interaction = Interaction(
        user_id=payload.user_id,
        item_id=payload.item_id,
        type=payload.type,
    )
    db.add(interaction)
    db.commit()
    return {"status": "ok", "type": payload.type, "item_id": payload.item_id}


@router.get("/saved")
def get_saved_items(db: Session = Depends(get_db)):
    """Return all items the user has saved, with full item data."""
    saved_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == 1, Interaction.type == "saved")
        .all()
    )

    item_ids = [i.item_id for i in saved_interactions]
    items = db.query(Item).filter(Item.id.in_(item_ids)).all() if item_ids else []

    return {
        "count": len(item_ids),
        "item_ids": item_ids,
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "author": item.author,
                "url": item.url,
                "published_at": item.published_at,
                "source_id": item.source_id,
            }
            for item in items
        ],
    }
