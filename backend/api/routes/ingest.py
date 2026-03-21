# backend/api/routes/ingest.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import SessionLocal
from backend.db.models import Source
from backend.services.ingestion import process_source

router = APIRouter()

CATEGORY_MAP = {
    "rss": "newsletters",
    "arxiv": "papers",
    "spotify": "podcasts",
    "youtube": "videos",
}

def _run_source(source_id: int):
    """Creates its own DB session — safe for background tasks."""
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return
        category = CATEGORY_MAP.get(source.type)
        if category:
            process_source(db, source, category)
    finally:
        db.close()

def _run_all():
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.enabled == True).all()
        source_ids = [(s.id,) for s in sources]  # capture IDs before session closes
    finally:
        db.close()
    
    for (source_id,) in source_ids:
        _run_source(source_id)

@router.post("/trigger/{source_id}")
def trigger_ingestion(source_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_source, source_id)
    return {"status": "ingestion_started", "source_id": source_id}

@router.post("/trigger-all")
def trigger_all_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_all)
    return {"status": "ingestion_started_for_all"}
