# backend/api/routes/digest.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.database import get_db
from backend.db.models import Item, ItemContent

router = APIRouter()


@router.get("/daily")
def get_daily_digest(db: Session = Depends(get_db)):
    """Get items from the last 24 hours."""
    cutoff = datetime.utcnow() - timedelta(days=1)

    items = db.query(Item).filter(
        Item.published_at >= cutoff
    ).order_by(Item.published_at.desc()).limit(50).all()

    return {
        "date": datetime.utcnow().date().isoformat(),
        "count": len(items),
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "author": item.author,
                "url": item.url,
                "published_at": item.published_at,
                "source_id": item.source_id
            }
            for item in items
        ]
    }

@router.get("/item/{item_id}")
def get_item_detail(item_id: int, db: Session = Depends(get_db)):
    """Get full item with content."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    content = db.query(ItemContent).filter(
        ItemContent.item_id == item_id
    ).first()
    
    return {
        "id": item.id,
        "title": item.title,
        "author": item.author,
        "url": item.url,
        "published_at": item.published_at,
        "content": content.parsed_content if content else None,
        "metadata": content.metadata_json if content else {}
    }
