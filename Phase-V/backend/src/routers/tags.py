from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from ..models.tag import Tag, TagCreate, TagUpdate
from ..schemas.tag import TagCreateRequest, TagUpdateRequest, TagResponse
from ..dependencies.auth_dependencies import get_current_user_id
from ..database import get_async_session
from ..services.tag_service import TagService
import uuid as uuid_lib


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagResponse])
async def list_tags(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all tags for the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    tag_service = TagService()
    tags = tag_service.get_user_tags(session, str(user_uuid))
    return tags


@router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreateRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new tag for the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    tag_service = TagService()
    tag = TagCreate(**tag_data.model_dump())
    created_tag = tag_service.create_tag(session, tag, str(user_uuid))
    return created_tag


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: uuid_lib.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific tag by ID.
    Only returns tags that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    tag_service = TagService()
    tag = tag_service.get_tag(session, str(tag_id), str(user_uuid))
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid_lib.UUID,
    tag_data: TagUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update an existing tag.
    Only allows updating tags that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    tag_service = TagService()
    updated_tag = tag_service.update_tag(session, str(tag_id), str(user_uuid), TagUpdate(**tag_data.model_dump()))
    
    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return updated_tag


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: uuid_lib.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete a tag.
    Only allows deleting tags that belong to the authenticated user.
    """
    try:
        user_uuid = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    tag_service = TagService()
    success = tag_service.delete_tag(session, str(tag_id), str(user_uuid))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return {"message": "Tag deleted successfully"}