from typing import List, Optional
from sqlmodel import Session, select
from ..models.priority import Priority, PriorityCreate, PriorityUpdate


class PriorityService:
    """
    Service class to handle priority management.
    """
    
    def create_priority(self, session: Session, priority_data: PriorityCreate) -> Priority:
        """
        Create a new priority level.
        """
        # Ensure value is within valid range (1-3)
        if priority_data.value < 1 or priority_data.value > 3:
            raise ValueError("Priority value must be between 1 and 3")
        
        db_priority = Priority.from_orm(priority_data)
        session.add(db_priority)
        session.commit()
        session.refresh(db_priority)
        return db_priority
    
    def get_priority(self, session: Session, priority_id: str) -> Optional[Priority]:
        """
        Get a priority by ID.
        """
        return session.get(Priority, priority_id)
    
    def get_all_priorities(self, session: Session) -> List[Priority]:
        """
        Get all priority levels.
        """
        statement = select(Priority)
        priorities = session.exec(statement).all()
        return priorities
    
    def update_priority(self, session: Session, priority_id: str, priority_data: PriorityUpdate) -> Optional[Priority]:
        """
        Update a priority level.
        """
        db_priority = session.get(Priority, priority_id)
        if db_priority:
            update_data = priority_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_priority, field, value)
            
            # Ensure value is within valid range (1-3)
            if hasattr(db_priority, 'value') and (db_priority.value < 1 or db_priority.value > 3):
                raise ValueError("Priority value must be between 1 and 3")
            
            session.add(db_priority)
            session.commit()
            session.refresh(db_priority)
        return db_priority
    
    def delete_priority(self, session: Session, priority_id: str) -> bool:
        """
        Delete a priority level.
        """
        db_priority = session.get(Priority, priority_id)
        if db_priority:
            session.delete(db_priority)
            session.commit()
            return True
        return False