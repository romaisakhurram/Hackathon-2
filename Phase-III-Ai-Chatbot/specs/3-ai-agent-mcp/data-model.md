# Data Model: AI Agent + MCP Integration

## Entities

### AI Agent Session
- **session_id** (string): Unique identifier for the conversation session
- **user_id** (string): Reference to authenticated user
- **context_window** (array): Last 5-10 conversation turns
- **created_at** (timestamp): Session creation time
- **last_activity** (timestamp): Last interaction time

### MCP Tool Request
- **request_id** (string): Unique identifier for the tool request
- **tool_name** (string): Name of the MCP tool being called (add_task, list_tasks, etc.)
- **parameters** (object): Parameters for the tool call
- **user_id** (string): Reference to authenticated user making request
- **auth_token** (string): JWT token for authenticating with backend API
- **timestamp** (timestamp): When the request was made
- **status** (string): Current status (pending, processing, completed, failed)
- **backend_response** (object): Response received from backend API call

### AI Intent Classification
- **intent_id** (string): Unique identifier for the intent
- **user_input** (string): Raw user input text
- **detected_intent** (string): Classified intent (CREATE_TASK, LIST_TASKS, UPDATE_TASK, COMPLETE_TASK, DELETE_TASK)
- **confidence_score** (float): Confidence level in intent classification (0.0-1.0)
- **extracted_parameters** (object): Parameters extracted from user input
- **timestamp** (timestamp): When intent was classified

### Backend API Mapping
- **mapping_id** (string): Unique identifier for the API mapping
- **mcp_tool_name** (string): Name of the MCP tool (add_task, list_tasks, etc.)
- **http_method** (string): HTTP method (GET, POST, PUT, PATCH, DELETE)
- **api_endpoint** (string): Backend API endpoint (/api/tasks/, /api/tasks/{id}, etc.)
- **parameter_mapping** (object): How MCP parameters map to API request body/query params
- **response_transformation** (object): How to transform backend response to MCP format

## Relationships
- AI Agent Session 1-* MCP Tool Request (session contains multiple tool requests)
- User 1-* AI Agent Session (user has multiple sessions)
- User 1-* MCP Tool Request (user makes multiple requests)
- Backend API Mapping 1-* MCP Tool Request (each request uses a mapping)

## Validation Rules
- All MCP tool requests must have a valid user_id
- Confidence score must be between 0.0 and 1.0
- Tool parameters must conform to the specific tool's schema
- User can only operate on their own tasks (ownership validation)
- Auth token must be present and valid for backend API calls
- Priority values must be converted between string (UI) and integer (backend) representations

## State Transitions
- MCP Tool Request: PENDING → PROCESSING → COMPLETED/SUCCESS or FAILED
- AI Agent Session: ACTIVE → INACTIVE (based on last_activity timeout)