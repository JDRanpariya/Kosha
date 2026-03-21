# backend/api/routes/ingest.py

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, ensure_user_exists
from backend.api.schemas import StatusResponse
from backend.core.constants import CATEGORY_MAP
from backend.core.logging import get_logger, set_correlation_id
from backend.db.database import SessionLocal
from backend.db.models import Source
from backend.services.ingestion import IngestionService

router = APIRouter()
logger = get_logger(__name__)


def _run_source(source_id: int) -> None:
    """Run ingestion for a single source (background task)."""
    set_correlation_id()
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if source:
            service = IngestionService(db)
            service.process_source(source)
    except Exception as e:
        logger.error(f"Background ingestion failed for source {source_id}: {e}")
    finally:
        db.close()


def _run_all() -> None:
    """Run ingestion for all enabled sources (background task)."""
    set_correlation_id()
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.enabled == True).all()
        source_ids = [s.id for s in sources]
    finally:
        db.close()
    
    for source_id in source_ids:
        _run_source(source_id)


@router.post("/trigger/{source_id}", response_model=StatusResponse)
def trigger_ingestion(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> StatusResponse:
    """Trigger ingestion for a single source."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return StatusResponse(status="error", message="Source not found")
    
    background_tasks.add_task(_run_source, source_id)
    return StatusResponse(
        status="ingestion_started",
        message=f"Ingestion started for source {source_id}",
    )


@router.post("/trigger-all", response_model=StatusResponse)
def trigger_all_ingestion(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(ensure_user_exists),
) -> StatusResponse:
    """Trigger ingestion for all enabled sources."""
    background_tasks.add_task(_run_all)
    return StatusResponse(
        status="ingestion_started_for_all",
        message="Ingestion started for all enabled sources",
    )
