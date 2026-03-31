# backend/api/routes/ingest.py

from fastapi import APIRouter, BackgroundTasks
from backend.db.database import SessionLocal
from backend.db.models import Source
from backend.services.ingestion import process_source

router = APIRouter()

# Maps source.type → registry category

CATEGORY_MAP: dict[str, str] = {
    # newsletters
    "rss":        "subscriptions",
    "substack":   "subscriptions",
    "email_imap": "subscriptions",
    # papers
    "arxiv":      "subscriptions",
    # social
    "hackernews": "discovery",
    "reddit":     "discovery",
    # videos
    "youtube":    "subscriptions",
}


def _run_source(source_id: int) -> None:
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return
        category = CATEGORY_MAP.get(source.type)
        if not category:
            return
        process_source(db, source, category)
    finally:
        db.close()


def _run_all() -> None:
    db = SessionLocal()
    try:
        source_ids = [
            s.id
            for s in db.query(Source).filter(Source.enabled == True).all()
        ]
    finally:
        db.close()

    for source_id in source_ids:
        _run_source(source_id)


@router.post("/trigger/{source_id}")
def trigger_ingestion(source_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_source, source_id)
    return {"status": "ingestion_started", "source_id": source_id}


@router.post("/trigger-all")
def trigger_all_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_all)
    return {"status": "ingestion_started_for_all"}
