from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid

# Import the TaskTagLink class directly for the relationship
from .tag import TaskTagLink

if TYPE_CHECKING:
    from .user import User
    from .reminder import Reminder
    from .recurrence_rule import RecurrenceRule
    from .tag import Tag


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.
    Belongs to a specific user; has title, description, priority level, status, and timestamps.
    Extended to support advanced features: due dates, reminders, recurrence, tags, etc.
    """
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    priority: int = Field(default=0)
    difficulty_level: str = Field(default="intermediate")  # beginner, intermediate, advanced
    status: str = Field(default="pending")  # pending, in-progress, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = Field(default=None)  # When the task is due
    completed_at: Optional[datetime] = Field(default=None)  # When the task was completed
    priority_id: Optional[uuid.UUID] = Field(default=None, foreign_key="priorities.id")  # Link to priority model
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")  # For recurring tasks
    recurrence_rule_id: Optional[uuid.UUID] = Field(default=None, foreign_key="recurrence_rules.id")  # Link to recurrence rules
    is_template: bool = Field(default=False)  # Whether this is a template for recurring tasks
    user_id: uuid.UUID = Field(nullable=False, index=True)  # Foreign key to user, indexed for performance

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    reminders: List["Reminder"] = Relationship(back_populates="task", cascade_delete=True)
    recurrence_rule: "RecurrenceRule" = Relationship(back_populates="task")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', user_id={self.user_id})>"