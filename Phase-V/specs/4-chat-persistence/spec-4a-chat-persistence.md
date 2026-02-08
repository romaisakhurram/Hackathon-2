# Spec 4A: Chat API & Persistence

## Overview
This specification defines the persistent storage and retrieval of chatbot conversations via a stateless API. The system will store all conversation messages in the database to ensure continuity after service restarts while maintaining a stateless server architecture.

## Clarifications

### Session 2026-01-22
- Q: Should the Message model store the user_id of the message sender? → A: Yes, store message sender's user_id to enable multi-user conversations and clear message ownership
- Q: What should be the basis for rate limiting implementation? → A: Per user_id to provide fair allocation based on authenticated user identity
- Q: How should the system handle database transactions when saving messages? → A: Separate atomic operations for each message to prevent partial saves and ensure data consistency

## Context
- Phase III AI agent and MCP integration is already complete
- This spec defines only chat persistence and stateless API implementation
- No manual coding is allowed
- This project uses Spec-Kit Plus
- JWT authentication is required for all endpoints
- All messages must be persisted in the database

## Scope

### Included
- Chat conversation persistence via database storage
- Stateless API design (no server-side session memory)
- Conversation and message models
- JWT authentication enforcement
- User isolation (users can only access their own conversations)
- Message history storage and retrieval

### Excluded
- Frontend UI details
- AI agent implementation details
- MCP tool specifics
- Database schema definition (implementation detail)

## Technical Constraints
- API Framework: FastAPI
- ORM: SQLModel
- Database: Neon PostgreSQL
- Auth: Better Auth with JWT
- Server must be stateless
- No server-side session memory
- All messages must be stored in DB

## Key Entities
- **User**: Person interacting with the chatbot system
- **Conversation**: Container for a series of related messages between user and AI agent
- **Message**: Individual communication (user input or AI response) within a conversation
- **JWT Token**: Authentication token for verifying user identity and ownership

## User Scenarios & Testing

### Primary Scenario: Persistent Chat Session
1. User sends a message to the chat endpoint with JWT token
2. System validates JWT and extracts user_id
3. System loads existing conversation or creates new one
4. System saves user's message to database
5. System processes message through AI agent and MCP tools
6. System saves AI response to database
7. System returns response with conversation_id and tool_calls
8. User can resume conversation later with same conversation_id

### Secondary Scenario: Conversation Continuity After Restart
1. User had ongoing conversation with conversation_id=123
2. Server restarts (loses any in-memory state)
3. User sends next message with conversation_id=123
4. System loads conversation from database
5. System continues conversation seamlessly

### Error Scenario: Unauthorized Access Attempt
1. User attempts to access conversation belonging to another user
2. System validates user_id from JWT against conversation ownership
3. System returns 403 Forbidden error
4. User receives appropriate error message

## Functional Requirements

### FR1: Authentication Requirements
- Must validate JWT token for all chat endpoints
- Must extract user_id from JWT token for ownership validation
- Must reject requests without valid JWT token
- Must ensure users can only access their own conversations

### FR2: Conversation Management
- Must create new conversation when conversation_id is not provided
- Must load existing conversation when conversation_id is provided
- Must validate conversation ownership (user can only access own conversations)
- Must generate unique conversation identifiers

### FR3: Message Persistence
- Must save all user messages to database with conversation_id, user_id, role, and content
- Must save all AI responses to database with conversation_id, user_id, role, and content
- Must maintain chronological order of messages within conversations
- Must store message timestamps for ordering and audit purposes

### FR4: Stateless Operation
- Must not store conversation context in server memory
- Must load entire conversation context from database for each request
- Must return conversation_id to client for continuation
- Must handle concurrent requests for same conversation without conflicts

### FR5: API Contract
- Must provide POST /api/{user_id}/chat endpoint
- Request body must accept optional conversation_id (int) and message (string)
- Response must include conversation_id (int), response (string), and tool_calls (array)
- Must return appropriate HTTP status codes (200 for success, 401 for auth failure, 403 for unauthorized access)

### FR6: Data Models
- **Conversation Model**: id (int), user_id (string), created_at (timestamp), updated_at (timestamp)
- **Message Model**: id (int), conversation_id (int), user_id (string), role (string - 'user'/'assistant'), content (string), created_at (timestamp)
- Must enforce foreign key relationship between Message and Conversation
- Must enforce user ownership validation at database level
- Must store the user_id of the message sender for clear ownership of individual messages

### FR7: Error Handling
- Must return appropriate error messages when JWT is invalid
- Must return 403 when user attempts to access another user's conversation
- Must handle database connection errors gracefully
- Must maintain atomicity for message saving operations

### FR8: Transaction Handling
- Must implement separate atomic operations for each message save to prevent partial saves
- Must ensure data consistency by treating user messages and AI responses as individual atomic units
- Must handle transaction failures gracefully without corrupting conversation state

### FR9: Rate Limiting
- Must implement rate limiting based on user_id to provide fair allocation for authenticated users
- Must apply standard rate limiting of 10 requests per minute per user to prevent abuse
- Must track rate limits per authenticated user identity rather than IP address

## Assumptions
- JWT tokens are properly signed and validated using Better Auth secret
- Database connection is available and reliable
- AI agent and MCP tools are accessible for processing user messages
- User_id from JWT token matches the format used in the existing system

## Success Criteria
- 100% of chat messages are persisted to database successfully
- Chat conversations resume correctly after server restarts
- No server-side memory is used for conversation state (fully stateless)
- All conversations are properly isolated by user ownership
- API response times remain under 5 seconds for typical requests
- Users can only access their own conversations (0% cross-user access)

## Dependencies
- Working Phase III AI agent and MCP integration
- Properly configured Better Auth JWT validation
- Available Neon PostgreSQL database connection
- MCP tools for processing user requests

## Assumptions (continued)
- Maximum message length is 2000 characters to prevent abuse while allowing sufficient space for user input
- Conversations are retained indefinitely unless explicitly deleted by the user
- Standard rate limiting of 10 requests per minute per user is applied to prevent abuse