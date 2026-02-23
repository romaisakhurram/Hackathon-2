from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select
from typing import Optional, Dict, Any
from ..models.user import User
from ..schemas.user import UserResponse, UserUpdate, UserProfileResponse
from ..dependencies.auth_dependencies import get_current_user_id
from ..database import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from datetime import datetime

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get the current user's profile information.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(User).where(User.id == user_uuid)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        is_active=user.is_active,
        consent_granted_at=user.consent_granted_at,
        consent_version=user.consent_version
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update the current user's profile information.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(User).where(User.id == user_uuid)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update only the fields that are provided
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    user.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active
    )


@router.get("/settings", response_model=Dict[str, Any])
async def get_user_settings(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get the current user's settings.
    This is a placeholder - in a real app, you'd have a separate Settings model.
    """
    # For now, return default settings
    # In a real implementation, you would fetch from a user_settings table
    return {
        "notifications": {
            "email": True,
            "push": True,
            "sms": False,
            "in_app": True
        },
        "theme": "system",
        "language": "en",
        "timezone": "UTC"
    }


@router.put("/settings", response_model=Dict[str, Any])
async def update_user_settings(
    settings_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update the current user's settings.
    This is a placeholder - in a real app, you'd have a separate Settings model.
    """
    # For now, just return the settings that were sent
    # In a real implementation, you would save to a user_settings table
    return {
        "message": "Settings updated successfully",
        "settings": settings_data
    }


@router.post("/export-data")
async def export_user_data(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Export all user data (GDPR/CCPA compliance).
    Returns a download URL for the exported data.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # In a real implementation, you would:
    # 1. Gather all user data (tasks, tags, etc.)
    # 2. Create a JSON/CSV export
    # 3. Generate a temporary download link
    
    # For now, return a placeholder response
    return {
        "message": "Data export initiated",
        "status": "processing",
        "download_url": None,
        "estimated_time": "5-10 minutes"
    }


@router.delete("/account")
async def delete_user_account(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete the current user's account (GDPR/CCPA right to erasure).
    This marks the user for deletion and anonymizes their data.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    statement = select(User).where(User.id == user_uuid)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Mark user for deletion (soft delete for compliance)
    user.is_active = False
    user.data_deletion_requested = True
    user.data_deletion_requested_at = datetime.utcnow()
    
    # Anonymize email
    user.email = f"deleted_{user.id}@deleted.local"
    user.name = "Deleted User"

    await session.commit()

    return {
        "message": "Account deletion requested. Your data will be removed within 30 days.",
        "status": "pending_deletion"
    }
