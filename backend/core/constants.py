# backend/core/constants.py

"""
Application-wide constants.
Single source of truth for magic values.
"""

# Default user ID until auth is implemented

DEFAULT_USER_ID: int = 1

# Content categories mapped from source types

CATEGORY_MAP: dict[str, str] = {
    "rss": "newsletters",
    "arxiv": "papers",
    "spotify": "podcasts",
    "youtube": "videos",
}

# Pagination defaults

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# Embedding model

EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION: int = 384
