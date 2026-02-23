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
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced
    status: str = "pending"  # pending, in-progress, completed, cancelled
    due_date: Optional[datetime] = None  # When the task is due
    parent_id: Optional[uuid.UUID] = None  # For recurring tasks
    recurrence_rule_id: Optional[uuid.UUID] = None  # Link to recurrence rules
    is_template: bool = False  # Whether this is a template for recurring tasks


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
    difficulty_level: Optional[str] = None  # beginner, intermediate, advanced
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    parent_id: Optional[uuid.UUID] = None
    recurrence_rule_id: Optional[uuid.UUID] = None
    is_template: Optional[bool] = None


class TaskResponse(TaskBase):
    """
    Schema for task response with additional fields.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None  # When the task was completed

    class Config:
        from_attributes = True