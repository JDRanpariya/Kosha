# backend/api/routes/search.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, ensure_user_exists
from backend.api.schemas import SearchResponse, SearchUnavailableResponse, ItemSummary
from backend.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.services.embedding import get_embedding_service

router = APIRouter()


@router.get(
    "/",
    response_model=SearchResponse | SearchUnavailableResponse,
)
def search_items(
    q: str = Query(..., min_length=2),
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    user_id: int = Depends(ensure_user_exists),
) -> SearchResponse | SearchUnavailableResponse:
    """Semantic search across all items using pgvector."""
    embedding_service = get_embedding_service()
    
    if not embedding_service.available:
        return SearchUnavailableResponse(
            error="Search not available (sentence-transformers not installed)",
            available=False,
        )
    
    # Generate embedding for query
    query_embedding = embedding_service.encode(q)
    if not query_embedding:
        return SearchUnavailableResponse(
            error="Failed to generate query embedding",
            available=False,
        )
    
    # pgvector cosine distance search
    results = db.execute(
        text("""
            SELECT i.id, i.title, i.author, i.url, i.published_at, i.source_id,
                   ic.parsed_content,
                   1 - (ic.embedding <=> :embedding::vector) as similarity
            FROM items i
            JOIN item_content ic ON i.id = ic.item_id
            WHERE ic.embedding IS NOT NULL
            ORDER BY ic.embedding <=> :embedding::vector
            LIMIT :limit
        """),
        {"embedding": str(query_embedding), "limit": limit}
    ).fetchall()
    
    items = [
        ItemSummary(
            id=r.id,
            title=r.title,
            author=r.author,
            url=r.url,
            published_at=r.published_at,
            source_id=r.source_id,
            preview=r.parsed_content[:200] if r.parsed_content else None,
            similarity=round(r.similarity, 3),
        )
        for r in results
    ]
    
    return SearchResponse(
        query=q,
        count=len(items),
        items=items,
    )
