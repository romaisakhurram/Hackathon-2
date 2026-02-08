from sqlmodel import SQLModel, Field
from typing import Optional
import uuid


class PriorityBase(SQLModel):
    name: str = Field(max_length=20, nullable=False)  # High, Medium, Low
    value: int = Field(nullable=False)  # 1=High, 2=Medium, 3=Low
    color: str = Field(max_length=7, nullable=False)  # Hex color format


class Priority(PriorityBase, table=True):
    """
    Priority model defining the importance levels for tasks.
    """
    __tablename__ = "priorities"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(SQLModel):
    name: Optional[str] = Field(max_length=20)
    value: Optional[int] = None
    color: Optional[str] = Field(max_length=7)