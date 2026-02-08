from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, func, or_, and_
from sqlalchemy.sql import text
from datetime import datetime
from ..models.task import Task
from ..models.tag import Tag
from ..models.priority import Priority
from ..models.user import User


class SearchService:
    """
    Service class to handle task search functionality.
    """
    
    def search_tasks(
        self, 
        session: Session, 
        user_id: str, 
        query: Optional[str] = None,
        status: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        due_date_range: Optional[Dict[str, datetime]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20
    ) -> List[Task]:
        """
        Search tasks with various filters and sorting options.
        """
        # Start with base query for user's tasks
        statement = select(Task).where(Task.user_id == user_id)
        
        # Apply text search if query provided
        if query:
            statement = statement.where(
                or_(
                    Task.title.contains(query),
                    Task.description.contains(query)
                )
            )
        
        # Apply status filter
        if status:
            statement = statement.where(Task.status.in_(status))
        
        # Apply priority filter
        if priorities:
            # Join with priority table to filter by priority name
            priority_ids = self._get_priority_ids_by_name(session, priorities)
            if priority_ids:
                statement = statement.where(Task.priority_id.in_(priority_ids))
        
        # Apply due date range filter
        if due_date_range:
            if due_date_range.get('from'):
                statement = statement.where(Task.due_date >= due_date_range['from'])
            if due_date_range.get('to'):
                statement = statement.where(Task.due_date <= due_date_range['to'])
        
        # Apply tag filter
        if tags:
            statement = self._apply_tag_filter(statement, tags)
        
        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == 'asc':
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())
        
        # Apply pagination
        offset = (page - 1) * limit
        statement = statement.offset(offset).limit(limit)
        
        # Execute query
        tasks = session.exec(statement).all()
        return tasks
    
    def _get_priority_ids_by_name(self, session: Session, priority_names: List[str]) -> List[str]:
        """
        Get priority IDs by their names.
        """
        statement = select(Priority.id).where(Priority.name.in_(priority_names))
        priority_ids = session.exec(statement).all()
        return priority_ids
    
    def _apply_tag_filter(self, statement, tag_names: List[str]):
        """
        Apply tag filter to the query.
        """
        # This is a simplified approach - in a real system you'd join with the tags table
        # and the task_tags junction table to filter by tag names
        from sqlalchemy import exists
        
        # For each tag name, we check if the task has that tag
        for tag_name in tag_names:
            statement = statement.where(
                exists().where(
                    and_(
                        Tag.name == tag_name,
                        Tag.id == TaskTagLink.tag_id,
                        TaskTagLink.task_id == Task.id
                    )
                )
            )
        
        return statement
    
    def get_search_statistics(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about user's tasks for search functionality.
        """
        # Count total tasks
        total_tasks_stmt = select(func.count(Task.id)).where(Task.user_id == user_id)
        total_tasks = session.exec(total_tasks_stmt).one()
        
        # Count tasks by status
        status_counts_stmt = select(Task.status, func.count(Task.id)).where(
            Task.user_id == user_id
        ).group_by(Task.status)
        status_counts = dict(session.exec(status_counts_stmt).all())
        
        # Count tasks by priority
        priority_counts_stmt = select(Priority.name, func.count(Task.id)).select_from(
            Task.__table__.join(Priority, Task.priority_id == Priority.id)
        ).where(Task.user_id == user_id).group_by(Priority.name)
        priority_counts = dict(session.exec(priority_counts_stmt).all())
        
        return {
            "total_tasks": total_tasks,
            "status_counts": status_counts,
            "priority_counts": priority_counts
        }