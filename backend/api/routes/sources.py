# backend/api/routes/sources.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, ensure_user_exists
from backend.api.schemas import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceListResponse,
    SourceCreatedResponse,
    StatusResponse,
)
from backend.db.models import Source

router = APIRouter()


@router.get("/", response_model=SourceListResponse)
def list_sources(
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> SourceListResponse:
    """List all sources."""
    sources = db.query(Source).all()
    return SourceListResponse(
        sources=[
            SourceResponse(
                id=s.id,
                name=s.name,
                type=s.type,
                url=s.url,
                enabled=s.enabled,
                last_fetched_at=s.last_fetched_at,
                config_json=s.config_json or {},
            )
            for s in sources
        ],
        count=len(sources),
    )


@router.post("/", status_code=201, response_model=SourceCreatedResponse)
def create_source(
    source: SourceCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> SourceCreatedResponse:
    """Create a new source."""
    db_source = Source(
        user_id=user_id,
        name=source.name,
        type=source.type,
        url=source.url,
        config_json=source.config_json,
        enabled=True,
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    return SourceCreatedResponse(id=db_source.id, name=db_source.name)


@router.patch("/{source_id}", response_model=StatusResponse)
def update_source(
    source_id: int,
    source: SourceUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> StatusResponse:
    """Update a source."""
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
    return StatusResponse(status="updated")


@router.delete("/{source_id}", response_model=StatusResponse)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> StatusResponse:
    """Delete a source."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(db_source)
    db.commit()
    return StatusResponse(status="deleted")
