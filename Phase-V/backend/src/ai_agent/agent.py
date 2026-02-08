"""
Main AI agent implementation for the Todo AI Chatbot.
Handles natural language processing and routes requests to appropriate MCP tools.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from openai import AsyncOpenAI

from ..config import settings as ai_config
from .intent_recognizer import IntentRecognizer
from .response_formatter import ResponseFormatter


logger = logging.getLogger(__name__)


class AIAgent:
    """
    AI Agent that interprets natural language from users and uses MCP tools to manage todos.
    """

    def __init__(self):
        """
        Initialize the AI Agent with OpenAI client and supporting components.
        """
        self.openai_client = AsyncOpenAI(
            api_key=ai_config.openai_api_key,
            base_url=ai_config.openai_base_url,
        )
        self.intent_recognizer = IntentRecognizer()
        self.response_formatter = ResponseFormatter()

        # Conversation context management
        self.conversation_contexts: Dict[str, list] = {}

    async def process_message(self, user_input: str, user_id: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Process a natural language message from a user and return an appropriate response.

        Args:
            user_input: The natural language message from the user
            user_id: The ID of the authenticated user
            conversation_id: The ID of the conversation (optional)

        Returns:
            Dictionary containing the response to send back to the user
        """
        try:
            # Use a combination of user_id and conversation_id as the context key
            # If no conversation_id is provided, just use user_id
            context_key = f"{user_id}_{conversation_id}" if conversation_id else user_id

            # Add user message to conversation context
            self._add_to_context(context_key, {"role": "user", "content": user_input})

            # Recognize intent from user input
            intent_result = await self.intent_recognizer.recognize_intent(
                user_input,
                self._get_context_window(context_key)
            )

            # Check confidence threshold
            if intent_result.confidence < ai_config.intent_confidence_threshold:
                # Ask for clarification if confidence is too low
                clarification_needed = await self._generate_clarification_request(user_input)
                return {
                    "type": "clarification",
                    "message": clarification_needed,
                    "original_input": user_input
                }

            # Map intent to appropriate MCP tool and execute
            result = await self._execute_intent(intent_result, user_id)

            # Format the response
            formatted_response = self.response_formatter.format_response(
                intent_result.intent_type,
                result,
                user_input
            )

            # Add response to conversation context
            self._add_to_context(context_key, {"role": "assistant", "content": formatted_response})

            return {
                "type": "success",
                "message": formatted_response,
                "action": intent_result.intent_type,
                "result": result
            }

        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            error_message = self.response_formatter.format_error(str(e))
            return {
                "type": "error",
                "message": error_message
            }

    async def _execute_intent(self, intent_result, user_id: UUID) -> Dict[str, Any]:
        """
        Execute the appropriate action based on the recognized intent.
        This method integrates with the MCP server tools.
        """
        try:
            # Call the appropriate MCP tool based on the intent type
            from ..mcp_server.server import MCPServer
            
            mcp_server = MCPServer()
            
            # Get the actual string value of the intent type
            # Handle both enum and string cases to be safe
            raw_intent_type = intent_result.intent_type
            print(f"DEBUG: Raw intent type: {raw_intent_type}, type: {type(raw_intent_type)}")

            if hasattr(raw_intent_type, 'value'):
                intent_type_value = raw_intent_type.value
                print(f"DEBUG: Extracted value: {intent_type_value}, type: {type(intent_type_value)}")
            else:
                # If it's already a string, use it directly
                intent_type_value = str(raw_intent_type)
                print(f"DEBUG: Converted to string: {intent_type_value}, type: {type(intent_type_value)}")

            # Ensure it's a string
            intent_type_value = str(intent_type_value)
            print(f"DEBUG: Final intent_type_value: {intent_type_value}")

            # Map intent types to MCP tool names
            intent_to_tool = {
                "add_task": "add_task",
                "list_tasks": "list_tasks",
                "update_task": "update_task",
                "complete_task": "complete_task",
                "delete_task": "delete_task"
            }

            tool_name = intent_to_tool.get(intent_type_value, intent_type_value)

            # Ensure tool_name is definitely a string before passing to execute_tool
            tool_name = str(tool_name)

            # Execute the MCP tool with parameters and user_id
            result = await mcp_server.execute_tool(
                tool_name,
                intent_result.parameters,
                str(user_id)
            )
            
            return result
        except Exception as e:
            logger.error(f"Error executing intent {intent_result.intent_type}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "intent": intent_result.intent_type
            }

    def _add_to_context(self, user_id: str, message: Dict[str, str]):
        """
        Add a message to the conversation context for a user.
        """
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = []

        self.conversation_contexts[user_id].append(message)

        # Maintain only the last N conversations as specified in requirements (5-10 turns)
        max_context = 10
        if len(self.conversation_contexts[user_id]) > max_context:
            self.conversation_contexts[user_id] = self.conversation_contexts[user_id][-max_context:]

    def _get_context_window(self, user_id: str) -> list:
        """
        Get the current conversation context window for a user.
        """
        return self.conversation_contexts.get(user_id, [])

    async def _generate_clarification_request(self, user_input: str) -> str:
        """
        Generate a clarification request when the AI agent is uncertain about the intent.
        """
        try:
            response = await self.openai_client.chat.completions.create(
                model=ai_config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that asks clarifying questions when user requests are ambiguous. Keep your questions concise and specific."
                    },
                    {
                        "role": "user",
                        "content": f"The user said: '{user_input}'. This was unclear. Please ask a clarifying question to understand what they want."
                    }
                ],
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating clarification: {str(e)}")
            return f"I'm not sure I understood. Could you clarify what you mean by '{user_input}'?"

    async def reset_context(self, user_id: str):
        """
        Reset the conversation context for a user.
        """
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id]