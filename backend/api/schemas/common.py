# backend/api/schemas/common.py

"""
Shared schema definitions.
"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model conversion
        populate_by_name=True,
    )


class StatusResponse(BaseSchema):
    """Generic status response."""
    status: str
    message: str | None = None


class PaginatedResponse(BaseSchema):
    """Base for paginated responses."""
    total: int
    limit: int
    offset: int
