from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class ReminderBase(BaseModel):
    """
    Base schema for reminder data.
    """
    task_id: uuid.UUID
    scheduled_time: datetime
    method: str = "in-app"  # email, push, sms, in-app


class ReminderCreateRequest(ReminderBase):
    """
    Schema for creating a new reminder.
    """
    pass


class ReminderUpdateRequest(BaseModel):
    """
    Schema for updating an existing reminder.
    """
    scheduled_time: Optional[datetime] = None
    method: Optional[str] = None
    sent: Optional[bool] = None


class ReminderResponse(ReminderBase):
    """
    Schema for reminder response with additional fields.
    """
    id: uuid.UUID
    sent: bool = False
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True