from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models.task import Task
from ..models.recurrence_rule import RecurrenceRule, RecurrenceRuleCreate, RecurrenceRuleUpdate
from ..models.user import User
from enum import Enum


class RecurrenceInterval(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurrenceService:
    """
    Service class to handle recurring task logic.
    """
    
    def create_recurrence_rule(self, session: Session, rule_data: RecurrenceRuleCreate) -> RecurrenceRule:
        """
        Create a new recurrence rule.
        """
        db_rule = RecurrenceRule.from_orm(rule_data)
        session.add(db_rule)
        session.commit()
        session.refresh(db_rule)
        return db_rule
    
    def get_recurrence_rule(self, session: Session, rule_id: str) -> Optional[RecurrenceRule]:
        """
        Get a recurrence rule by ID.
        """
        return session.get(RecurrenceRule, rule_id)
    
    def update_recurrence_rule(self, session: Session, rule_id: str, rule_data: RecurrenceRuleUpdate) -> Optional[RecurrenceRule]:
        """
        Update a recurrence rule.
        """
        db_rule = session.get(RecurrenceRule, rule_id)
        if db_rule:
            update_data = rule_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_rule, field, value)
            
            session.add(db_rule)
            session.commit()
            session.refresh(db_rule)
        return db_rule
    
    def delete_recurrence_rule(self, session: Session, rule_id: str) -> bool:
        """
        Delete a recurrence rule.
        """
        db_rule = session.get(RecurrenceRule, rule_id)
        if db_rule:
            session.delete(db_rule)
            session.commit()
            return True
        return False
    
    def generate_next_occurrences(self, session: Session, task: Task, count: int = 5) -> List[Task]:
        """
        Generate the next occurrences of a recurring task based on its recurrence rule.
        """
        if not task.recurrence_rule:
            return []
        
        rule = task.recurrence_rule
        occurrences = []
        current_date = datetime.now()
        
        # Start from the last generated occurrence or from the task's creation date
        start_date = task.created_at
        if hasattr(task, 'last_generated_date'):
            start_date = task.last_generated_date
        
        for i in range(count):
            next_date = self._calculate_next_occurrence(start_date, rule)
            if next_date and (not rule.end_date or next_date <= rule.end_date):
                # Create a new task instance based on the template
                new_task = Task(
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    status="pending",
                    user_id=task.user_id,
                    due_date=next_date,
                    parent_id=task.id,  # Link to the original recurring task
                    is_template=False  # This is an instance, not a template
                )
                
                session.add(new_task)
                occurrences.append(new_task)
                start_date = next_date
            else:
                break
        
        session.commit()
        return occurrences
    
    def _calculate_next_occurrence(self, start_date: datetime, rule: RecurrenceRule) -> Optional[datetime]:
        """
        Calculate the next occurrence date based on the recurrence rule.
        """
        if rule.interval == RecurrenceInterval.DAILY:
            return start_date + timedelta(days=rule.frequency)
        elif rule.interval == RecurrenceInterval.WEEKLY:
            return start_date + timedelta(weeks=rule.frequency)
        elif rule.interval == RecurrenceInterval.MONTHLY:
            # For monthly recurrence, we need to handle varying month lengths
            # This is a simplified approach - in a real system, you'd want more sophisticated date handling
            import calendar
            year = start_date.year
            month = start_date.month + rule.frequency
            
            # Handle year overflow
            while month > 12:
                year += 1
                month -= 12
            
            # Get the number of days in the target month
            max_day = calendar.monthrange(year, month)[1]
            day = min(start_date.day, max_day)
            
            return start_date.replace(year=year, month=month, day=day)
        elif rule.interval == RecurrenceInterval.YEARLY:
            return start_date.replace(year=start_date.year + rule.frequency)
        elif rule.interval == RecurrenceInterval.CUSTOM:
            # For custom intervals, we could support more complex patterns
            # For now, treat as daily with custom frequency
            return start_date + timedelta(days=rule.frequency)
        
        return None