# backend/api/dependencies.py

"""
Shared FastAPI dependencies.
"""

from typing import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.core.constants import DEFAULT_USER_ID
from backend.core.logging import set_correlation_id, get_logger
from backend.db.database import SessionLocal
from backend.db.models import User

logger = get_logger(__name__)


def get_db() -> Generator[Session, None, None]:
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_correlation_id_from_request(request: Request) -> str:
    """Extract or generate correlation ID from request headers."""
    # Check for incoming correlation ID header
    cid = request.headers.get("X-Correlation-ID")
    return set_correlation_id(cid)


def get_current_user_id(
    request: Request,
    db: Session = Depends(get_db),
) -> int:
    """
    Get current user ID.
    
    For now, returns DEFAULT_USER_ID. Later, this will:
    1. Extract JWT from Authorization header
    2. Validate and decode token
    3. Return actual user ID

    """
    # TODO: Implement actual auth
    # token = request.headers.get("Authorization")
    # if token:
    #     user_id = decode_jwt(token)
    #     return user_id
    
    return DEFAULT_USER_ID


def ensure_user_exists(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> int:
    """
    Ensure the user exists in the database.
    Creates default user if needed (for development).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.info(f"Creating default user with id={user_id}")
        user = User(id=user_id, email=f"user{user_id}@kosha.local")
        db.add(user)
        db.commit()
    return user_id
