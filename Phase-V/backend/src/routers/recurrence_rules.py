from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from ..models.recurrence_rule import RecurrenceRule, RecurrenceRuleCreate, RecurrenceRuleUpdate, RecurrenceInterval
from ..schemas.recurrence_rule import RecurrenceRuleCreateRequest, RecurrenceRuleUpdateRequest, RecurrenceRuleResponse
from ..dependencies.auth_dependencies import get_current_user_id
from ..database import get_async_session
from ..services.recurrence_service import RecurrenceService
import uuid as uuid_lib


router = APIRouter(prefix="/recurrence-rules", tags=["recurrence-rules"])


@router.post("/", response_model=RecurrenceRuleResponse)
async def create_recurrence_rule(
    recurrence_rule_data: RecurrenceRuleCreateRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new recurrence rule for a task.
    Only allows creating recurrence rules for tasks that belong to the authenticated user.
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
    statement = select(Task).where(Task.id == recurrence_rule_data.task_id, Task.user_id == user_uuid)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )
    
    recurrence_service = RecurrenceService()
    recurrence_rule = RecurrenceRuleCreate(**recurrence_rule_data.model_dump())
    created_recurrence_rule = recurrence_service.create_recurrence_rule(session, recurrence_rule)
    return created_recurrence_rule


@router.get("/{recurrence_rule_id}", response_model=RecurrenceRuleResponse)
async def get_recurrence_rule(
    recurrence_rule_id: uuid_lib.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific recurrence rule by ID.
    Only returns recurrence rules for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.recurrence_rule import RecurrenceRule
    from ..models.task import Task
    statement = select(RecurrenceRule).join(
        RecurrenceRule.task
    ).where(
        RecurrenceRule.id == recurrence_rule_id,
        Task.user_id == user_uuid
    )
    result = await session.execute(statement)
    recurrence_rule = result.scalar_one_or_none()
    
    if not recurrence_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence rule not found"
        )
    
    return recurrence_rule


@router.put("/{recurrence_rule_id}", response_model=RecurrenceRuleResponse)
async def update_recurrence_rule(
    recurrence_rule_id: uuid_lib.UUID,
    recurrence_rule_data: RecurrenceRuleUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update an existing recurrence rule.
    Only allows updating recurrence rules for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.recurrence_rule import RecurrenceRule
    from ..models.task import Task
    statement = select(RecurrenceRule).join(
        RecurrenceRule.task
    ).where(
        RecurrenceRule.id == recurrence_rule_id,
        Task.user_id == user_uuid
    )
    result = await session.execute(statement)
    recurrence_rule = result.scalar_one_or_none()
    
    if not recurrence_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence rule not found"
        )
    
    recurrence_service = RecurrenceService()
    updated_recurrence_rule = recurrence_service.update_recurrence_rule(
        session, 
        str(recurrence_rule_id), 
        RecurrenceRuleUpdate(**recurrence_rule_data.model_dump(exclude_unset=True))
    )
    
    if not updated_recurrence_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence rule not found"
        )
    
    return updated_recurrence_rule


@router.delete("/{recurrence_rule_id}")
async def delete_recurrence_rule(
    recurrence_rule_id: uuid_lib.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete a recurrence rule.
    Only allows deleting recurrence rules for tasks that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    from sqlmodel import select
    from ..models.recurrence_rule import RecurrenceRule
    from ..models.task import Task
    statement = select(RecurrenceRule).join(
        RecurrenceRule.task
    ).where(
        RecurrenceRule.id == recurrence_rule_id,
        Task.user_id == user_uuid
    )
    result = await session.execute(statement)
    recurrence_rule = result.scalar_one_or_none()
    
    if not recurrence_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence rule not found"
        )
    
    recurrence_service = RecurrenceService()
    success = recurrence_service.delete_recurrence_rule(session, str(recurrence_rule_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence rule not found"
        )
    
    return {"message": "Recurrence rule deleted successfully"}