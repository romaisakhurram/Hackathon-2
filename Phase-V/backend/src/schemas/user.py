from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """
    Base schema for user data.
    """
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    """
    email: Optional[str] = None
    name: Optional[str] = None


class UserResponse(UserBase):
    """
    Schema for user response.
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """
    Schema for user profile response with additional details.
    """
    id: uuid.UUID
    email: str
    name: Optional[str] = None
    created_at: datetime
    is_active: bool
    consent_granted_at: Optional[datetime] = None
    consent_version: Optional[str] = None

    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    """
    Schema for user settings.
    """
    notifications: Optional[dict] = None
    theme: str = "system"
    language: str = "en"
    timezone: str = "UTC"
