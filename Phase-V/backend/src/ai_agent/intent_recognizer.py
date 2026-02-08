"""
Intent recognition logic for the AI agent.
Identifies user intents from natural language input.
"""
import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

from openai import AsyncOpenAI

from ..config import settings as ai_config


logger = logging.getLogger(__name__)


class IntentType(Enum):
    """
    Types of intents that the AI agent can recognize.
    """
    ADD_TASK = "add_task"
    LIST_TASKS = "list_tasks"
    UPDATE_TASK = "update_task"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """
    Result of intent recognition.
    """
    intent_type: IntentType
    confidence: float
    parameters: Dict[str, Any]
    extracted_text: str


class IntentRecognizer:
    """
    Handles the recognition of user intents from natural language input.
    """

    def __init__(self):
        """
        Initialize the intent recognizer.
        """
        self.openai_client = AsyncOpenAI(
            api_key=ai_config.openai_api_key,
            base_url=ai_config.openai_base_url,
        )

    def _try_simple_pattern_match(self, user_input: str) -> Optional[IntentResult]:
        """
        Try to match simple patterns without needing OpenAI API.
        This allows basic intent recognition even if API fails.
        
        Args:
            user_input: The user's input text
            
        Returns:
            IntentResult if a simple pattern matches, None otherwise
        """
        user_lower = user_input.lower()
        
        # Add task patterns
        if any(phrase in user_lower for phrase in ["add task", "add a task", "create task", "new task", "add the task", "add to do"]):
            # Extract task title from the input
            title = user_input
            for phrase in ["add task", "add a task", "create task", "new task", "add the task", "add to do"]:
                if phrase in user_lower:
                    # Get text after the phrase
                    idx = user_lower.find(phrase)
                    title = user_input[idx + len(phrase):].strip()
                    break
            
            return IntentResult(
                intent_type=IntentType.ADD_TASK,
                confidence=0.9,  # High confidence for simple patterns
                parameters={"title": title if title else "Untitled Task", "description": ""},
                extracted_text=user_input
            )
        
        # List tasks patterns
        if any(phrase in user_lower for phrase in ["list tasks", "show tasks", "what tasks", "get tasks", "my tasks", "all tasks"]):
            return IntentResult(
                intent_type=IntentType.LIST_TASKS,
                confidence=0.95,
                parameters={},
                extracted_text=user_input
            )
        
        # Complete/mark done patterns with ID extraction
        if any(phrase in user_lower for phrase in ["complete task", "done", "finished", "mark complete", "check off"]):
            # Try to extract task ID from the input
            # Look for patterns like "#1", "task 1", "task #1", "id: abc123", etc.
            id_patterns = [
                r'#(\d+)',  # Matches #1, #2, etc.
                r'task\s+#?\s*(\d+)',  # Matches "task 1", "task #1", "task#1", etc.
                r'id[:\s]+([a-zA-Z0-9-]+)'  # Matches "id: abc123", "id 123abc", etc.
            ]

            task_identifier = None
            for pattern in id_patterns:
                match = re.search(pattern, user_lower)
                if match:
                    task_identifier = match.group(1)
                    break

            parameters = {}
            if task_identifier:
                # If it's a numeric identifier, treat it as a task index
                if task_identifier.isdigit():
                    parameters["task_index"] = int(task_identifier)
                else:
                    # Otherwise, treat it as a task ID
                    parameters["task_id"] = task_identifier

            return IntentResult(
                intent_type=IntentType.COMPLETE_TASK,
                confidence=0.85,
                parameters=parameters,
                extracted_text=user_input
            )
        
        # Delete patterns
        if any(phrase in user_lower for phrase in ["delete task", "remove task", "remove", "delete"]):
            return IntentResult(
                intent_type=IntentType.DELETE_TASK,
                confidence=0.85,
                parameters={},
                extracted_text=user_input
            )
        
        return None

    async def recognize_intent(self, user_input: str, context: List[Dict[str, str]] = None) -> IntentResult:
        """
        Recognize the intent from user input.

        Args:
            user_input: The natural language input from the user
            context: Previous conversation context for better understanding

        Returns:
            IntentResult containing the recognized intent and parameters
        """
        # First, try to match simple patterns - much faster and more reliable
        simple_match = self._try_simple_pattern_match(user_input)
        if simple_match:
            logger.info(f"Intent recognized via simple pattern match: {simple_match.intent_type}")
            return simple_match
        
        try:
            # Prepare the system message for intent classification
            system_message = {
                "role": "system",
                "content": f"""You are a task management assistant. Classify the user's intent and extract parameters.

Recognized intents:
- add_task: Adding a new task
- list_tasks: Requesting to see tasks
- update_task: Modifying an existing task
- complete_task: Marking a task as completed
- delete_task: Removing a task

Return your response in JSON format with these fields:
- intent_type: The recognized intent (add_task, list_tasks, update_task, complete_task, delete_task, unknown)
- confidence: A float between 0 and 1 indicating confidence in the classification
- parameters: An object containing extracted parameters like task title, description, priority, task_id, etc.
- extracted_text: The text that was analyzed

Example response format:
{{"intent_type": "add_task", "confidence": 0.95, "parameters": {{"title": "Buy groceries", "priority": "medium"}}, "extracted_text": "Add a task to buy groceries"}}

Be precise with confidence scores - only assign high confidence when you're certain about the intent."""
            }

            # Prepare messages with context if available
            messages = [system_message]

            if context:
                # Include conversation context to help with understanding
                for msg in context[-5:]:  # Use last 5 messages as context
                    messages.append(msg)

            # Add the user's current input
            messages.append({"role": "user", "content": user_input})

            # Call OpenAI API to classify intent
            response = await self.openai_client.chat.completions.create(
                model=ai_config.openai_model,
                messages=messages,
                max_tokens=200,
                temperature=0.1,  # Low temperature for more consistent classification
                response_format={"type": "json_object"}  # Force JSON response
            )

            # Parse the response
            response_content = response.choices[0].message.content.strip()

            # Clean up potential prefixes/suffixes
            if response_content.startswith("```json"):
                response_content = response_content[7:]
            if response_content.endswith("```"):
                response_content = response_content[:-3]
            response_content = response_content.strip()

            parsed_response = json.loads(response_content)

            # Validate the response structure
            intent_type_str = parsed_response.get("intent_type", "unknown")
            confidence = parsed_response.get("confidence", 0.0)
            parameters = parsed_response.get("parameters", {})
            extracted_text = parsed_response.get("extracted_text", user_input)

            # Convert string intent to enum
            try:
                intent_type = IntentType(intent_type_str)
            except ValueError:
                intent_type = IntentType.UNKNOWN
                confidence = 0.0  # Lower confidence if intent type is invalid

            # Ensure confidence is within bounds
            confidence = max(0.0, min(1.0, confidence))

            return IntentResult(
                intent_type=intent_type,
                confidence=confidence,
                parameters=parameters,
                extracted_text=extracted_text
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from OpenAI: {e}")
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.3,  # Low confidence for parsing errors
                parameters={},
                extracted_text=user_input
            )
        except Exception as e:
            logger.error(f"Error recognizing intent for input '{user_input}': {str(e)}")
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.2,  # Very low confidence for other errors
                parameters={},
                extracted_text=user_input
            )

    def extract_task_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extract task-related parameters from text using simpler heuristics.
        This is a fallback method if the AI classification fails.
        """
        params = {}

        # Look for common priority indicators
        text_lower = text.lower()
        if "high" in text_lower:
            params["priority"] = "high"
        elif "medium" in text_lower:
            params["priority"] = "medium"
        elif "low" in text_lower:
            params["priority"] = "low"

        # Extract task title (basic approach)
        # This is a simplified approach - in practice, you'd want more sophisticated NLP
        params["title"] = text.strip()

        return params