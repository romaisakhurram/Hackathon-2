from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session, delete
from typing import List, Optional, Dict, Any
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..dependencies.auth_dependencies import get_current_user_id
from ..database import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_
import uuid
from datetime import datetime
from ..services.search_service import SearchService


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all tasks for the authenticated user.
    Implements user data isolation by filtering all queries by user_id from the authenticated user's token.
    """
    import uuid as uuid_lib
    from sqlalchemy import desc, asc

    # Convert string user_id to UUID for comparison with Task.user_id
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Validate sort_by parameter to prevent SQL injection
    valid_sort_columns = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "title": Task.title
    }
    order_column = valid_sort_columns.get(sort_by, Task.created_at)

    # Apply sorting
    if sort_order == "asc":
        statement = select(Task).where(Task.user_id == user_uuid).order_by(asc(order_column))
    else:
        statement = select(Task).where(Task.user_id == user_uuid).order_by(desc(order_column))

    # Apply pagination
    offset = (page - 1) * limit
    statement = statement.offset(offset).limit(limit)

    results = await session.execute(statement)
    tasks = results.scalars().all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific task by ID.
    Only returns tasks that belong to the authenticated user.
    """
    import uuid as uuid_lib

    # Convert string user_id to UUID for comparison with Task.user_id
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
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
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new task for the authenticated user.
    Assigns the current user's user_id to ensure data isolation (FR-002).
    """
    import uuid as uuid_lib
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Convert string user_id to UUID for Task.user_id
        try:
            user_uuid = uuid_lib.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        logger.info(f"Creating task for user {user_id}: {task_data.title}")

        # Create task with the authenticated user's ID
        task = Task(
            **task_data.model_dump(),
            user_id=user_uuid
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        logger.info(f"Task created successfully: {task.id}")
        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update an existing task.
    Only allows updating tasks that belong to the authenticated user.
    """
    import uuid as uuid_lib

    # Convert string user_id to UUID for comparison with Task.user_id
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
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
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete a task.
    Only allows deleting tasks that belong to the authenticated user.
    """
    import uuid as uuid_lib

    # Convert string user_id to UUID for comparison with Task.user_id
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
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
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Toggle the completion status of a task.
    Only allows toggling tasks that belong to the authenticated user.
    """
    import uuid as uuid_lib

    # Convert string user_id to UUID for comparison with Task.user_id
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
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


@router.post("/search", response_model=List[TaskResponse])
async def search_tasks(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Search tasks with various filters.
    """
    import uuid as uuid_lib

    # Convert string user_id to UUID for comparison with Task.user_id
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    search_service = SearchService()
    
    # Prepare filters
    status_filter = filters.get('status') if filters else None
    priority_filter = filters.get('priorities') if filters else None
    tag_filter = filters.get('tags') if filters else None
    due_date_range = filters.get('dueDateRange') if filters else None
    
    tasks = search_service.search_tasks(
        session=session,
        user_id=str(user_uuid),
        query=query,
        status=status_filter,
        priorities=priority_filter,
        tags=tag_filter,
        due_date_range=due_date_range,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )
    
    return tasks