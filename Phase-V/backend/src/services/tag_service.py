from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models.tag import Tag, TagCreate, TagUpdate, TaskTagLink
from ..models.user import User
from ..models.task import Task


class TagService:
    """
    Service class to handle tag management.
    """
    
    def create_tag(self, session: Session, tag_data: TagCreate, user_id: str) -> Tag:
        """
        Create a new tag for a user.
        """
        db_tag = Tag.from_orm(tag_data)
        db_tag.user_id = user_id  # Associate with the user
        session.add(db_tag)
        session.commit()
        session.refresh(db_tag)
        return db_tag
    
    def get_tag(self, session: Session, tag_id: str, user_id: str) -> Optional[Tag]:
        """
        Get a tag by ID for a specific user.
        """
        statement = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        return session.exec(statement).first()
    
    def get_user_tags(self, session: Session, user_id: str) -> List[Tag]:
        """
        Get all tags for a specific user.
        """
        statement = select(Tag).where(Tag.user_id == user_id, Tag.deleted_at.is_(None))
        tags = session.exec(statement).all()
        return tags
    
    def update_tag(self, session: Session, tag_id: str, user_id: str, tag_data: TagUpdate) -> Optional[Tag]:
        """
        Update a tag for a specific user.
        """
        db_tag = self.get_tag(session, tag_id, user_id)
        if db_tag:
            update_data = tag_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_tag, field, value)
            
            session.add(db_tag)
            session.commit()
            session.refresh(db_tag)
        return db_tag
    
    def delete_tag(self, session: Session, tag_id: str, user_id: str) -> bool:
        """
        Soft delete a tag for a specific user (remove associations but keep tag data).
        """
        db_tag = self.get_tag(session, tag_id, user_id)
        if db_tag:
            # Remove all associations with tasks
            statement = select(TaskTagLink).where(TaskTagLink.tag_id == tag_id)
            associations = session.exec(statement).all()
            for assoc in associations:
                session.delete(assoc)
            
            # Mark tag as deleted
            db_tag.deleted_at = datetime.utcnow()
            session.add(db_tag)
            session.commit()
            return True
        return False
    
    def add_tag_to_task(self, session: Session, task_id: str, tag_id: str) -> bool:
        """
        Add a tag to a task.
        """
        # Check if association already exists
        statement = select(TaskTagLink).where(
            TaskTagLink.task_id == task_id,
            TaskTagLink.tag_id == tag_id
        )
        existing_assoc = session.exec(statement).first()
        
        if existing_assoc:
            return True  # Already associated
        
        # Create new association
        task_tag_link = TaskTagLink(task_id=task_id, tag_id=tag_id)
        session.add(task_tag_link)
        session.commit()
        return True
    
    def remove_tag_from_task(self, session: Session, task_id: str, tag_id: str) -> bool:
        """
        Remove a tag from a task.
        """
        statement = select(TaskTagLink).where(
            TaskTagLink.task_id == task_id,
            TaskTagLink.tag_id == tag_id
        )
        assoc = session.exec(statement).first()
        
        if assoc:
            session.delete(assoc)
            session.commit()
            return True
        return False
    
    def get_task_tags(self, session: Session, task_id: str) -> List[Tag]:
        """
        Get all tags associated with a task.
        """
        statement = (
            select(Tag)
            .join(TaskTagLink)
            .where(TaskTagLink.task_id == task_id)
        )
        tags = session.exec(statement).all()
        return tags