# backend/api/routes/sources.py - Add these endpoints

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Source

router = APIRouter()

class SourceCreate(BaseModel):
    name: str
    type: str  # 'rss', 'arxiv', 'spotify', 'youtube'
    url: str | None = None
    config_json: dict = {}

class SourceUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    config_json: dict | None = None

@router.get("/")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.type,
            "url": s.url,
            "enabled": s.enabled,
            "last_fetched_at": s.last_fetched_at,
            "config": s.config_json,
        }
        for s in sources
    ]

@router.post("/", status_code=201)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    db_source = Source(
        name=source.name,
        type=source.type,
        url=source.url,
        config_json=source.config_json,
        enabled=True,
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return {"id": db_source.id, "name": db_source.name}

@router.patch("/{source_id}")
def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.name is not None:
        db_source.name = source.name
    if source.enabled is not None:
        db_source.enabled = source.enabled
    if source.config_json is not None:
        db_source.config_json = source.config_json
    
    db.commit()
    return {"status": "updated"}

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(db_source)
    db.commit()
    return {"status": "deleted"}
