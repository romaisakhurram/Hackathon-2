from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session, delete
from typing import List
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..dependencies import get_current_user_id, validate_token_expiration
from ..database import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_
import uuid
from datetime import datetime


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all tasks for the authenticated user.
    Implements user data isolation by filtering all queries by user_id from the authenticated user's token.
    """
    # Query tasks filtered by user_id to ensure data isolation (FR-002)
    statement = select(Task).where(Task.user_id == user_id)
    results = await session.execute(statement)
    tasks = results.scalars().all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific task by ID.
    Only returns tasks that belong to the authenticated user.
    """
    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    results = await session.execute(statement)
    task = results.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new task for the authenticated user.
    Assigns the current user's user_id to ensure data isolation (FR-002).
    """
    # Create task with the authenticated user's ID
    task = Task(
        **task_data.model_dump(),
        user_id=user_id
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update an existing task.
    Only allows updating tasks that belong to the authenticated user.
    """
    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    results = await session.execute(statement)
    task = results.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update only the fields that are provided
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update the timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete a task.
    Only allows deleting tasks that belong to the authenticated user.
    """
    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    results = await session.execute(statement)
    task = results.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await session.delete(task)
    await session.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Toggle the completion status of a task.
    Only allows toggling tasks that belong to the authenticated user.
    """
    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    results = await session.execute(statement)
    task = results.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle the status between 'pending' and 'completed'
    if task.status == 'pending':
        task.status = 'completed'
    else:
        task.status = 'pending'

    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return task