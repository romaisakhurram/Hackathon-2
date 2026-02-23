from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
import uuid
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .task import Task


class ReminderMethod(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in-app"


class ReminderBase(SQLModel):
    task_id: uuid.UUID = Field(foreign_key="tasks.id", nullable=False)
    scheduled_time: datetime = Field(nullable=False)
    method: ReminderMethod = Field(default=ReminderMethod.IN_APP, nullable=False)


class Reminder(ReminderBase, table=True):
    """
    Reminder model for task notifications.
    """
    __tablename__ = "reminders"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sent: bool = Field(default=False)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to task
    task: "Task" = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={
            "foreign_keys": "[Reminder.task_id]"
        }
    )


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(SQLModel):
    scheduled_time: Optional[datetime] = None
    method: Optional[ReminderMethod] = None
    sent: Optional[bool] = None