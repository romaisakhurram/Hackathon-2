from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from ..models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderMethod
from ..schemas.reminder import ReminderCreateRequest, ReminderUpdateRequest, ReminderResponse
from ..dependencies.auth_dependencies import get_current_user_id
from ..database import get_async_session
from ..services.reminder_service import ReminderService
import uuid as uuid_lib
from datetime import datetime, timedelta


router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    reminder_data: ReminderCreateRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new reminder for a task.
    Only allows creating reminders for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Verify that the task belongs to the user
    from sqlmodel import select
    from ..models.task import Task
    statement = select(Task).where(Task.id == reminder_data.task_id, Task.user_id == user_uuid)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )
    
    reminder_service = ReminderService()
    reminder = ReminderCreate(**reminder_data.model_dump())
    created_reminder = reminder_service.create_reminder(session, reminder)
    return created_reminder


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: uuid_lib.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific reminder by ID.
    Only returns reminders for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.reminder import Reminder
    statement = select(Reminder).join(
        Reminder.task
    ).where(
        Reminder.id == reminder_id,
        Task.user_id == user_uuid
    )
    result = await session.execute(statement)
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: uuid_lib.UUID,
    reminder_data: ReminderUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update an existing reminder.
    Only allows updating reminders for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.reminder import Reminder
    from ..models.task import Task
    statement = select(Reminder).join(
        Reminder.task
    ).where(
        Reminder.id == reminder_id,
        Task.user_id == user_uuid
    )
    result = await session.execute(statement)
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    reminder_service = ReminderService()
    updated_reminder = reminder_service.update_reminder(
        session, 
        str(reminder_id), 
        ReminderUpdate(**reminder_data.model_dump(exclude_unset=True))
    )
    
    if not updated_reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return updated_reminder


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: uuid_lib.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete a reminder.
    Only allows deleting reminders for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.reminder import Reminder
    from ..models.task import Task
    statement = select(Reminder).join(
        Reminder.task
    ).where(
        Reminder.id == reminder_id,
        Task.user_id == user_uuid
    )
    result = await session.execute(statement)
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    reminder_service = ReminderService()
    success = reminder_service.delete_reminder(session, str(reminder_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return {"message": "Reminder deleted successfully"}


@router.get("/upcoming/", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    within_minutes: int = 5,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all upcoming reminders for the authenticated user within the specified time window.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.reminder import Reminder
    from ..models.task import Task
    statement = select(Reminder).join(
        Reminder.task
    ).where(
        Reminder.scheduled_time <= datetime.utcnow() + timedelta(minutes=within_minutes),
        Reminder.sent == False,
        Task.user_id == user_uuid
    ).order_by(Reminder.scheduled_time.asc())
    
    result = await session.execute(statement)
    reminders = result.scalars().all()
    
    return reminders