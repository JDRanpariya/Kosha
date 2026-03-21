# backend/api/routes/search.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.db.database import get_db
from backend.db.models import Item, ItemContent

router = APIRouter()

# Load model once at startup

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    SEARCH_ENABLED = True
except ImportError:
    SEARCH_ENABLED = False

@router.get("/")
def search_items(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db)
):
    """Semantic search across all items using pgvector."""
    if not SEARCH_ENABLED:
        return {"error": "Search not available (sentence-transformers not installed)"}
    
    # Generate embedding for query
    query_embedding = _model.encode(q).tolist()
    
    # pgvector cosine distance search
    results = db.execute(
        text("""
            SELECT i.id, i.title, i.author, i.url, i.published_at,
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
    
    return {
        "query": q,
        "count": len(results),
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "author": r.author,
                "url": r.url,
                "published_at": r.published_at,
                "preview": r.parsed_content[:200] if r.parsed_content else None,
                "similarity": round(r.similarity, 3)
            }
            for r in results
        ]
    }
