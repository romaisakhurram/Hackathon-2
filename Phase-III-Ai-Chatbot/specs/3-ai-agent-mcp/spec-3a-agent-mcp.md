# Spec 3A: AI Agent + MCP Integration

## Overview
This specification defines the AI agent logic and MCP server integration for the Todo AI Chatbot project. The AI agent will interpret natural language from users and use MCP tools to manage todos through the existing backend APIs.

## Context
- Phase II frontend and backend are already complete
- This spec defines only AI agent logic and MCP server integration
- No manual coding is allowed
- OpenRouter must be used instead of a paid OpenAI key
- All task operations already exist in backend APIs

## Scope

### Included
- AI agent responsibilities
- MCP server role
- Tool definitions and constraints
- Agent behavior rules
- Error handling rules
- Acceptance criteria

### Excluded
- Frontend UI details
- Chat endpoint persistence logic
- Database schema definitions

## Technical Constraints
- AI Framework: OpenAI Agents SDK (OpenAI-compatible via OpenRouter)
- MCP Server: Official MCP SDK
- Backend: FastAPI
- ORM: SQLModel
- Database: Neon PostgreSQL
- Auth: Better Auth
- Server must be stateless

## Key Entities
- User: Person interacting with the AI chatbot
- AI Agent: Natural language processing system that interprets user requests
- MCP Server: Service that exposes tools for the AI agent to interact with the backend
- Task: Todo item managed through the system

## User Scenarios & Testing

### Primary Scenario: Natural Language Todo Management
1. User sends natural language request (e.g., "Add a task to buy groceries")
2. AI agent interprets the intent and extracts relevant parameters
3. AI agent calls appropriate MCP tool (e.g., add_task)
4. MCP server validates user ownership and executes backend API call
5. Result is returned to the user in natural language format

### Secondary Scenario: Task Listing
1. User sends request to see tasks (e.g., "Show me my tasks")
2. AI agent recognizes listing intent
3. AI agent calls list_tasks MCP tool
4. MCP server validates user ownership and retrieves user's tasks
5. Tasks are formatted and returned to user naturally

### Error Scenario: Invalid Task Operation
1. User requests operation on non-existent task
2. AI agent attempts MCP tool call
3. MCP server returns error
4. AI agent responds with appropriate natural language error message

## Functional Requirements

### FR1: AI Agent Responsibilities
- Must interpret natural language user requests
- Must determine appropriate MCP tool to call based on user intent
- Must extract parameters from natural language input
- Must format responses in natural language
- Must never access database directly
- Must use only MCP tools for all task operations

### FR2: MCP Server Role
- Must expose standardized tools for AI agent consumption
- Must validate user ownership for all operations
- Must be stateless and not store user session data
- Must forward requests to existing backend APIs
- Must handle authentication using JWT tokens

### FR3: MCP Tool Definitions

#### add_task
- **Purpose**: Create a new task for the authenticated user
- **Parameters**:
  - title (string, required): The task title/description
  - priority (string, optional): Priority level (low, medium, high)
  - due_date (string, optional): Due date in ISO format
- **Return shape**: Object with id (string), title (string), completed (boolean), priority (string), due_date (string, nullable), created_at (timestamp)
- **Ownership validation rule**: Only the authenticated user who owns the task can create it

#### list_tasks
- **Purpose**: Retrieve all tasks for the authenticated user
- **Parameters**: None
- **Return shape**: Array of task objects with id (string), title (string), completed (boolean), priority (string), due_date (string, nullable), created_at (timestamp)
- **Ownership validation rule**: Only returns tasks owned by the authenticated user

#### update_task
- **Purpose**: Modify an existing task for the authenticated user
- **Parameters**:
  - task_id (string, required): ID of the task to update
  - title (string, optional): New task title/description
  - priority (string, optional): New priority level
  - due_date (string, optional): New due date in ISO format
  - completed (boolean, optional): Completion status
- **Return shape**: Updated task object with id (string), title (string), completed (boolean), priority (string), due_date (string, nullable), updated_at (timestamp)
- **Ownership validation rule**: Only the authenticated user who owns the task can update it

#### complete_task
- **Purpose**: Mark a task as completed for the authenticated user
- **Parameters**:
  - task_id (string, optional): ID of the task to mark as completed
  - task_index (integer, optional): Index of the task in the user's task list (1-based)
- **Return shape**: Updated task object with id (string), title (string), completed (boolean), priority (string), due_date (string, nullable), updated_at (timestamp)
- **Ownership validation rule**: Only the authenticated user who owns the task can mark it as completed
- **Additional behavior**: If task_id is not provided, the system will attempt to use task_index to identify the task; if a numeric task_id is provided, it will be treated as a task_index

#### delete_task
- **Purpose**: Remove a task for the authenticated user
- **Parameters**:
  - task_id (string, required): ID of the task to delete
- **Return shape**: Boolean indicating successful deletion
- **Ownership validation rule**: Only the authenticated user who owns the task can delete it

### FR4: Agent Behavior Rules
- Must infer intent from natural language
- Must use MCP tools for all task mutations
- Must never access DB directly
- Must confirm every successful action
- Must handle missing tasks gracefully
- Must ask for clarification only when required
- Must maintain conversation context where appropriate
- Must provide helpful error messages when operations fail

### FR5: Error Handling Rules
- Must gracefully handle MCP tool failures
- Must provide user-friendly error messages
- Must handle invalid task IDs appropriately
- Must handle unauthorized access attempts
- Must handle malformed natural language input
- Must handle rate limiting from OpenRouter API

## Assumptions
- Backend APIs for task operations are already implemented and functioning
- Authentication is handled through JWT tokens passed with each request
- User identification is maintained through the authentication system
- OpenRouter API is properly configured and accessible

## Success Criteria
- 95% of natural language requests are correctly interpreted and mapped to appropriate MCP tools
- All task operations initiated through the AI agent complete successfully within 5 seconds
- Zero direct database access occurs from the AI agent
- All user data remains properly isolated based on ownership
- Users can successfully perform all task operations (create, read, update, delete) using natural language
- Error handling maintains 99% uptime for the AI agent service
- AI agent successfully rejects requests for tasks belonging to other users

## Dependencies
- Working Phase II frontend and backend systems
- Properly configured OpenRouter API access
- MCP SDK installation and setup
- JWT authentication tokens available for user context

## Clarifications

### Session 2026-01-20
- Q: What format should the AI agent use when providing error messages to users? → A: Abstract format (user-friendly without technical details)
- Q: What should be the timeout duration for MCP tool calls? → A: 30 seconds
- Q: How many previous conversation turns should the AI agent maintain for context? → A: 5-10 turns
- Q: Should the system use the same model for all requests or vary the model based on complexity? → A: Same model for all requests
- Q: What confidence threshold should trigger clarification requests versus proceeding with the assumed intent? → A: 80% confidence

## Additional Functional Requirements

### FR6: Error Message Format
- Must provide user-friendly error messages without exposing technical system details
- Must maintain consistent tone and language appropriate for non-technical users
- Must focus on what the user can do to resolve the issue, if applicable

### FR7: MCP Tool Timeout
- All MCP tool calls must have a timeout of 30 seconds
- If a tool call exceeds the timeout, the AI agent must return an appropriate error message to the user
- The timeout should be configurable for operational flexibility

### FR8: Conversation Context Management
- The AI agent must maintain context from the previous 5-10 conversation turns
- Context should include user intent, task references, and relevant conversation history
- Older context may be summarized or discarded to maintain performance

### FR9: AI Model Consistency
- The system must use the same AI model for all user requests
- Model selection should be consistent to ensure predictable behavior
- The specific model should be configurable via environment variables

### FR10: Intent Confidence Management
- The AI agent must operate with an 80% confidence threshold for taking actions
- When confidence is below 80%, the agent must ask the user for clarification
- When confidence is 80% or higher, the agent may proceed with the assumed intent