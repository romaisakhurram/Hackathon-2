from typing import List, Optional
import logging
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderMethod
from ..models.task import Task
from ..models.user import User
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from .email_service import EmailService

logger = logging.getLogger(__name__)


class ReminderService:
    """
    Service class to handle reminder scheduling and notifications.
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.email_service = EmailService()

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

    async def send_reminder_notification(self, session: Session, reminder: Reminder) -> bool:
        """
        Send a reminder notification based on the reminder method.
        
        Args:
            session: Database session
            reminder: The reminder to send
            
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Get the task associated with this reminder
            task = session.get(Task, reminder.task_id)
            if not task:
                logger.error(f"Task not found for reminder {reminder.id}: {reminder.task_id}")
                return False

            # Get the user's email
            user = session.get(User, task.user_id)
            if not user or not user.email:
                logger.error(f"User or email not found for task {task.id}")
                return False

            # Send notification based on method
            if reminder.method == ReminderMethod.EMAIL:
                success = await self.email_service.send_task_reminder(
                    recipient_email=user.email,
                    task_title=task.title,
                    task_description=task.description,
                    due_date=task.due_date,
                    reminder_time=reminder.scheduled_time
                )
                return success
            elif reminder.method == ReminderMethod.PUSH:
                # TODO: Implement push notification
                logger.info(f"Push notification would be sent for task {task.id}")
                return True
            elif reminder.method == ReminderMethod.SMS:
                # TODO: Implement SMS notification
                logger.info(f"SMS notification would be sent for task {task.id}")
                return True
            elif reminder.method == ReminderMethod.IN_APP:
                # In-app notification (just log for now)
                logger.info(f"In-app notification for task {task.id}")
                return True
            else:
                logger.error(f"Unknown reminder method: {reminder.method}")
                return False

        except Exception as e:
            logger.error(f"Failed to send reminder notification: {str(e)}")
            return False

    def schedule_reminder_check(self, session: Session, callback_func):
        """
        Schedule a periodic check for upcoming reminders.
        This is a simplified implementation - in production, you'd want a more robust scheduling system.
        """
        def check_and_notify():
            upcoming_reminders = self.get_upcoming_reminders(session, within_minutes=1)
            for reminder in upcoming_reminders:
                # Send the actual notification
                asyncio.run(self.send_reminder_notification(session, reminder))

                # Mark as sent after notification is processed
                self.mark_reminder_as_sent(session, reminder.id)

        # Run the check in a separate thread
        self.executor.submit(check_and_notify)