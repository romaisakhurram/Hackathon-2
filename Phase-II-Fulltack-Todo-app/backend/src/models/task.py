from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
from datetime import datetime
import uuid


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.
    Belongs to a specific user; has title, description, priority level, status, and timestamps.
    """
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    priority: int = Field(default=0)
    status: str = Field(default="pending")  # pending, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: uuid.UUID = Field(nullable=False, index=True)  # Foreign key to user, indexed for performance

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', user_id={self.user_id})>"