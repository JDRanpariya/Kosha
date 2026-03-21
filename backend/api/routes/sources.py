# backend/api/routes/sources.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Source

router = APIRouter()

@router.get("/")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.type,
            "enabled": s.enabled,
            "last_fetched_at": s.last_fetched_at,
        }
        for s in sources
    ]
