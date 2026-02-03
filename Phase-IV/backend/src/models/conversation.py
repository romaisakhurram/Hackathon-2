"""
Conversation model for the chat persistence feature.
Represents a container for a series of related messages between user and AI agent.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
import uuid


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a container for related messages between user and AI agent.
    """
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(nullable=False, index=True)  # Reference to the user who owns this conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: Optional[str] = Field(default=None, max_length=255)  # Optional title for the conversation

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete-orphan"})