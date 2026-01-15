from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class TaskBase(BaseModel):
    """
    Base schema for task data.
    """
    title: str
    description: Optional[str] = None
    priority: int = 0
    status: str = "pending"  # pending, completed


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class TaskResponse(TaskBase):
    """
    Schema for task response with additional fields.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True