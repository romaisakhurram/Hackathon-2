from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column

if TYPE_CHECKING:
    from .task import Task


class RecurrenceInterval(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurrenceRuleBase(SQLModel):
    interval: RecurrenceInterval = Field(default=RecurrenceInterval.DAILY)
    frequency: int = Field(default=1, ge=1)  # How many intervals between recurrences
    days_of_week: Optional[str] = Field(default=None)  # For weekly: stored as comma-separated string (0=Sunday, 1=Monday, etc.)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)  # For monthly
    end_date: Optional[datetime] = Field(default=None)  # When recurrence stops
    occurrence_count: Optional[int] = Field(default=None, ge=1)  # Max occurrences (alternative to end_date)


class RecurrenceRule(RecurrenceRuleBase, table=True):
    """
    RecurrenceRule model defining patterns for recurring tasks.
    """
    __tablename__ = "recurrence_rules"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to task (one-to-one with tasks)
    task: "Task" = Relationship(back_populates="recurrence_rule")


class RecurrenceRuleCreate(RecurrenceRuleBase):
    pass


class RecurrenceRuleUpdate(SQLModel):
    interval: Optional[RecurrenceInterval] = None
    frequency: Optional[int] = None
    days_of_week: Optional[str] = None
    day_of_month: Optional[int] = None
    end_date: Optional[datetime] = None
    occurrence_count: Optional[int] = None