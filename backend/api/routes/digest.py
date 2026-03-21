# backend/api/routes/digest.py

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.dependencies import get_db, ensure_user_exists
from backend.api.schemas import DigestResponse, ItemDetailResponse, ItemSummary, ItemDetail
from backend.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.services.items import ItemService

from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/daily", response_model=DigestResponse)
def get_daily_digest(
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
) -> DigestResponse:
    """Get items from the last 24 hours with pagination."""
    service = ItemService(db)
    items, total = service.get_recent(hours=24, limit=limit, offset=offset)
    
    return DigestResponse(
        date=date.today(),
        total=total,
        limit=limit,
        offset=offset,
        items=[ItemService.to_summary(item) for item in items],
    )


@router.get("/item/{item_id}", response_model=ItemDetailResponse)
def get_item_detail(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> ItemDetailResponse:
    """Get full item with content."""
    service = ItemService(db)
    result = service.get_with_content(item_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item, content = result
    return ItemDetailResponse(item=ItemService.to_detail(item, content))
