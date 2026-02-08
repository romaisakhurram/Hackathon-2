from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
import uuid
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .user import User


class TagBase(SQLModel):
    name: str = Field(max_length=50, nullable=False)
    color: str = Field(max_length=7, default="#000000")  # Hex color format


class Tag(TagBase, table=True):
    """
    Tag model for categorizing tasks.
    """
    __tablename__ = "tags"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)  # For soft deletes
    
    # Relationship to user
    user: "User" = Relationship(back_populates="tags")


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = Field(max_length=50)
    color: Optional[str] = Field(max_length=7)


class TaskTagLink(SQLModel, table=True):
    """
    Junction table for many-to-many relationship between tasks and tags.
    """
    __tablename__ = "task_tags"
    
    task_id: uuid.UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)