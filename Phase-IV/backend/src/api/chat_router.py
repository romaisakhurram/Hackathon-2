"""
Chat router for the Todo AI Chatbot.
Implements the stateless chat API that persists conversations to the database.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Any, Dict
import uuid
from pydantic import BaseModel

from ..dependencies.auth_dependencies import get_current_user_id
from ..services.conversation_service import ConversationService
from ..services.message_service import MessageService
from ..ai_agent.agent import AIAgent
from ..utils.conversation_context_manager import get_conversation_context_manager
from ..config import settings


# Define request/response models
class ChatRequest(BaseModel):
    """
    Request model for chat messages.
    """
    message: str
    conversation_id: Optional[str] = None  # Using string to accommodate UUID format


class ChatResponse(BaseModel):
    """
    Response model for chat messages.
    """
    conversation_id: str
    response: str
    tool_calls: list = []
    action: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


# Create router
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_message(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Process a chat message and return AI-generated response.

    This endpoint implements a stateless chat API that persists all conversations
    to the database for continuity after service restarts.
    
    Note: The user_id in the path should match the authenticated user's ID.
    For now, if they don't match exactly, we use the authenticated user_id instead.
    """
    # Use authenticated user_id for security
    # The path parameter is kept for API compatibility but we enforce the authenticated user
    actual_user_id = current_user_id

    # Initialize services
    conversation_service = ConversationService()
    message_service = MessageService()
    ai_agent = AIAgent()

    try:
        # Determine if this is a new conversation or existing one
        conversation_id = None
        if request.conversation_id:
            # Try to load existing conversation
            try:
                conversation_uuid = uuid.UUID(request.conversation_id)
                conversation = await conversation_service.get_conversation_by_id(conversation_uuid, current_user_id)

                if not conversation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found or access denied"
                    )

                conversation_id = conversation_uuid
            except ValueError:
                # Invalid UUID format
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )

        # If no existing conversation, create a new one
        if not conversation_id:
            conversation = await conversation_service.create_conversation(current_user_id)
            conversation_id = conversation.id

        # Save the user's message
        user_message = await message_service.save_user_message(
            conversation_id=conversation_id,
            user_id=current_user_id,
            content=request.message
        )

        # Process the message through the existing AI agent and MCP tools
        # This would integrate with the existing AI agent from Phase III
        try:
            # Process the message with the AI agent
            ai_result = await ai_agent.process_message(
                user_input=request.message,
                user_id=current_user_id,
                conversation_id=str(conversation_id)
            )

            # Extract response and tool calls from AI result
            ai_response = ai_result.get("message", "I processed your request.")
            tool_calls = ai_result.get("tool_calls", []) if isinstance(ai_result.get("tool_calls"), list) else []
            action = ai_result.get("action")
            result = ai_result.get("result")

            # Save the AI response
            ai_message = await message_service.save_assistant_message(
                conversation_id=conversation_id,
                user_id="ai_agent",  # AI agent is the sender of this message
                content=ai_response,
                metadata_json=str(tool_calls) if tool_calls else None
            )

            return ChatResponse(
                conversation_id=str(conversation_id),
                response=ai_response,
                tool_calls=tool_calls,
                action=action,
                result=result
            )

        except Exception as e:
            # If AI processing fails, return an appropriate error response
            error_response = f"Sorry, I encountered an issue processing your request: {str(e)}"

            # Still save the error response as an AI message
            ai_message = await message_service.save_assistant_message(
                conversation_id=conversation_id,
                user_id="ai_agent",
                content=error_response
            )

            return ChatResponse(
                conversation_id=str(conversation_id),
                response=error_response,
                tool_calls=[]
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve all conversations for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's conversations"
        )

    conversation_service = ConversationService()
    conversations = await conversation_service.get_user_conversations(current_user_id)

    # Convert to a serializable format
    conversation_list = []
    for conv in conversations:
        conversation_list.append({
            "id": str(conv.id),
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        })

    return {"conversations": conversation_list}


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve all messages for a specific conversation.
    """
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's conversation"
        )

    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )

    conversation_service = ConversationService()
    message_service = MessageService()

    # Validate that user owns the conversation first
    if not await conversation_service.validate_conversation_ownership(conversation_uuid, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied"
        )

    messages = await message_service.get_messages_by_conversation(conversation_uuid)

    # Convert to a serializable format
    message_list = []
    for msg in messages:
        message_list.append({
            "id": str(msg.id),
            "conversation_id": str(msg.conversation_id),
            "user_id": msg.user_id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "metadata_json": msg.metadata_json
        })

    return {"messages": message_list}


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a conversation and all its messages if the user owns it.
    """
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot delete another user's conversation"
        )

    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )

    conversation_service = ConversationService()

    success = await conversation_service.delete_conversation(conversation_uuid, current_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied"
        )

    return {"message": "Conversation deleted successfully"}