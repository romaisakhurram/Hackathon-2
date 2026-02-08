from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class TagBase(BaseModel):
    """
    Base schema for tag data.
    """
    name: str
    color: str = "#000000"  # Default to black


class TagCreateRequest(TagBase):
    """
    Schema for creating a new tag.
    """
    pass


class TagUpdateRequest(BaseModel):
    """
    Schema for updating an existing tag.
    """
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    """
    Schema for tag response with additional fields.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None  # For soft deletes

    class Config:
        from_attributes = True