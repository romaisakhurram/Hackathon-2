from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderMethod
from ..models.task import Task
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


class ReminderService:
    """
    Service class to handle reminder scheduling and notifications.
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def create_reminder(self, session: Session, reminder_data: ReminderCreate) -> Reminder:
        """
        Create a new reminder.
        """
        db_reminder = Reminder.from_orm(reminder_data)
        session.add(db_reminder)
        session.commit()
        session.refresh(db_reminder)
        return db_reminder
    
    def get_reminder(self, session: Session, reminder_id: str) -> Optional[Reminder]:
        """
        Get a reminder by ID.
        """
        return session.get(Reminder, reminder_id)
    
    def get_upcoming_reminders(self, session: Session, within_minutes: int = 5) -> List[Reminder]:
        """
        Get all reminders scheduled within the specified time window.
        """
        cutoff_time = datetime.utcnow() + timedelta(minutes=within_minutes)
        statement = select(Reminder).where(
            Reminder.scheduled_time <= cutoff_time,
            Reminder.sent == False
        ).order_by(Reminder.scheduled_time.asc())
        
        reminders = session.exec(statement).all()
        return reminders
    
    def update_reminder(self, session: Session, reminder_id: str, reminder_data: ReminderUpdate) -> Optional[Reminder]:
        """
        Update a reminder.
        """
        db_reminder = session.get(Reminder, reminder_id)
        if db_reminder:
            update_data = reminder_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_reminder, field, value)
            
            session.add(db_reminder)
            session.commit()
            session.refresh(db_reminder)
        return db_reminder
    
    def delete_reminder(self, session: Session, reminder_id: str) -> bool:
        """
        Delete a reminder.
        """
        db_reminder = session.get(Reminder, reminder_id)
        if db_reminder:
            session.delete(db_reminder)
            session.commit()
            return True
        return False
    
    def mark_reminder_as_sent(self, session: Session, reminder_id: str) -> bool:
        """
        Mark a reminder as sent.
        """
        db_reminder = session.get(Reminder, reminder_id)
        if db_reminder:
            db_reminder.sent = True
            db_reminder.sent_at = datetime.utcnow()
            session.add(db_reminder)
            session.commit()
            session.refresh(db_reminder)
            return True
        return False
    
    def schedule_reminder_check(self, session: Session, callback_func):
        """
        Schedule a periodic check for upcoming reminders.
        This is a simplified implementation - in production, you'd want a more robust scheduling system.
        """
        def check_and_notify():
            upcoming_reminders = self.get_upcoming_reminders(session, within_minutes=1)
            for reminder in upcoming_reminders:
                # In a real implementation, this would send the actual notification
                # based on the reminder.method (email, push, sms, etc.)
                print(f"Scheduling notification for task {reminder.task_id} at {reminder.scheduled_time}")
                
                # Mark as sent after notification is processed
                self.mark_reminder_as_sent(session, reminder.id)
        
        # Run the check in a separate thread
        self.executor.submit(check_and_notify)