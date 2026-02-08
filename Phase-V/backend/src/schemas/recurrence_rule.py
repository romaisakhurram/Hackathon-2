from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class RecurrenceRuleBase(BaseModel):
    """
    Base schema for recurrence rule data.
    """
    task_id: uuid.UUID
    interval: str  # daily, weekly, monthly, yearly, custom
    frequency: int = 1  # How many intervals between recurrences
    days_of_week: Optional[List[int]] = None  # For weekly: 0=Sunday, 1=Monday, etc.
    day_of_month: Optional[int] = None  # For monthly
    end_date: Optional[datetime] = None  # When recurrence stops
    occurrence_count: Optional[int] = None  # Max occurrences (alternative to end_date)


class RecurrenceRuleCreateRequest(RecurrenceRuleBase):
    """
    Schema for creating a new recurrence rule.
    """
    pass


class RecurrenceRuleUpdateRequest(BaseModel):
    """
    Schema for updating an existing recurrence rule.
    """
    interval: Optional[str] = None
    frequency: Optional[int] = None
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    end_date: Optional[datetime] = None
    occurrence_count: Optional[int] = None


class RecurrenceRuleResponse(RecurrenceRuleBase):
    """
    Schema for recurrence rule response with additional fields.
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True