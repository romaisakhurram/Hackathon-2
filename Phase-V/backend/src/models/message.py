"""
Message model for the chat persistence feature.
Represents individual communications (user input or AI response) within a conversation.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid


class Message(SQLModel, table=True):
    """
    Message model representing individual communications (user input or AI response) within a conversation.
    """
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: str = Field(nullable=False)  # ID of the user who sent this message (sender)
    role: str = Field(nullable=False, max_length=20)  # Role of the message sender ('user' for human, 'assistant' for AI agent)
    content: str = Field(max_length=2000, nullable=False)  # The actual message content
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_json: Optional[str] = Field(default=None)  # Additional metadata for the message (e.g., tool calls, response details)

    # Relationship to conversation
    conversation: "Conversation" = Relationship(
        back_populates="messages",
        sa_relationship_kwargs={
            "foreign_keys": "[Message.conversation_id]"
        }
    )