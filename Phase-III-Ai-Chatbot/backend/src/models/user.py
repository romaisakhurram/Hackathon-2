from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """
    User model representing an authenticated user of the system.
    Implements GDPR/CCPA compliance measures per BR-002.
    """
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, nullable=False, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    # GDPR/CCPA compliance fields
    consent_granted_at: Optional[datetime] = Field(default=None)
    consent_version: Optional[str] = Field(default=None, max_length=20)
    data_deletion_requested: bool = Field(default=False)
    data_deletion_requested_at: Optional[datetime] = Field(default=None)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

    def request_data_deletion(self):
        """
        Mark the user's data for deletion as per GDPR/CCPA rights.
        """
        self.data_deletion_requested = True
        self.data_deletion_requested_at = datetime.utcnow()

    def has_consent(self) -> bool:
        """
        Check if user has granted consent for data processing.
        """
        return self.consent_granted_at is not None