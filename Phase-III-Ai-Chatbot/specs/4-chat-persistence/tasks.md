# Tasks: Chat API & Persistence

**Feature**: Chat API & Persistence
**Branch**: `4-chat-persistence` | **Date**: 2026-01-22 | **Spec**: [spec-4a-chat-persistence.md](./spec-4a-chat-persistence.md)

## Overview

Implementation of a stateless chat API that persists conversations to the database for continuity after service restarts. The system stores all conversation messages in the database while maintaining a stateless server architecture. The API enforces JWT-based authentication and user isolation, ensuring users can only access their own conversations. The implementation integrates with the existing AI agent and MCP tools for processing user messages.

## Dependencies

- Working Phase III AI agent and MCP integration
- Properly configured Better Auth JWT validation
- Available Neon PostgreSQL database connection
- MCP tools for processing user requests

## Parallel Execution Opportunities

- Models can be developed in parallel (Conversation and Message models)
- Services can be developed in parallel after models are complete
- API endpoints can be developed in parallel with services
- Unit tests can be written in parallel with implementation

## Implementation Strategy

MVP approach: Start with basic chat endpoint that can handle message persistence and retrieval, then incrementally add authentication, rate limiting, and advanced features.

---

## Phase 1: Setup and Project Initialization

- [X] T001 Create project directory structure per implementation plan
- [X] T002 Update backend requirements.txt with new dependencies for chat persistence
- [X] T003 Create initial __init__.py files for new modules
- [X] T004 [P] Create models __init__.py in backend/src/models/__init__.py
- [X] T005 [P] Create services __init__.py in backend/src/services/__init__.py
- [X] T006 [P] Create api __init__.py in backend/src/api/__init__.py
- [X] T007 [P] Create middleware __init__.py in backend/src/middleware/__init__.py
- [X] T008 [P] Create dependencies __init__.py in backend/src/dependencies/__init__.py

## Phase 2: Foundational Components

- [X] T009 Create Conversation model in backend/src/models/conversation.py
- [X] T010 Create Message model in backend/src/models/message.py
- [X] T011 Create database indexes for efficient queries
- [X] T012 Implement JWT validation and user_id extraction in backend/src/dependencies/auth_dependencies.py
- [X] T013 Create basic conversation service in backend/src/services/conversation_service.py
- [X] T014 Create basic message service in backend/src/services/message_service.py

## Phase 3: [US1] Persistent Chat Session

**User Story Goal**: Enable users to send messages to the chat endpoint and receive AI responses while persisting the conversation to the database.

**Independent Test Criteria**:
- Given a user sends a message to the chat endpoint with JWT token
- When the system validates JWT and extracts user_id
- Then it should create/load conversation, save user message, process with AI agent, save AI response, and return response with conversation_id and tool_calls

**Tasks**:

- [X] T015 [P] [US1] Implement conversation creation and loading in conversation_service.py
- [X] T016 [P] [US1] Implement message persistence in message_service.py
- [X] T017 [US1] Create chat router with POST /api/{user_id}/chat endpoint in backend/src/api/chat_router.py
- [X] T018 [US1] Integrate with existing AI agent for message processing
- [X] T019 [US1] Implement message saving for user input
- [X] T020 [US1] Implement message saving for AI responses
- [X] T021 [US1] Return conversation_id, response, and tool_calls in proper format

## Phase 4: [US2] Conversation Continuity After Restart

**User Story Goal**: Ensure chat conversations can resume correctly after server restarts by loading conversation context from database.

**Independent Test Criteria**:
- Given a user had ongoing conversation with conversation_id=123
- When server restarts (loses any in-memory state) and user sends next message with conversation_id=123
- Then the system should load conversation from database and continue seamlessly

**Tasks**:

- [X] T022 [US2] Implement conversation loading from database for existing conversation_id
- [X] T023 [US2] Validate conversation ownership against authenticated user
- [X] T024 [US2] Ensure stateless operation (no server-side session memory)
- [X] T025 [US2] Implement proper conversation context loading for each request
- [X] T026 [US2] Test conversation continuity after simulated server restart

## Phase 5: [US3] Unauthorized Access Prevention

**User Story Goal**: Prevent users from accessing conversations belonging to other users by validating user_id from JWT against conversation ownership.

**Independent Test Criteria**:
- Given a user attempts to access conversation belonging to another user
- When system validates user_id from JWT against conversation ownership
- Then it should return 403 Forbidden error with appropriate error message

**Tasks**:

- [X] T027 [US3] Implement conversation ownership validation in conversation_service.py
- [X] T028 [US3] Add user_id validation to message retrieval functions
- [X] T029 [US3] Return 403 Forbidden for unauthorized access attempts
- [X] T030 [US3] Create appropriate error messages for unauthorized access
- [X] T031 [US3] Test access restriction between different user accounts

## Phase 6: [US4] Advanced Features and Error Handling

**User Story Goal**: Enhance the system with rate limiting, transaction handling, and comprehensive error handling.

**Independent Test Criteria**:
- Given various error conditions (invalid JWT, database errors, rate limit exceeded)
- When users interact with the chat API
- Then the system should handle errors gracefully with appropriate responses

**Tasks**:

- [X] T032 [US4] Implement rate limiting middleware in backend/src/middleware/rate_limiter.py
- [X] T033 [US4] Apply rate limiting of 10 requests per minute per user_id
- [X] T034 [US4] Implement separate atomic operations for message saves
- [X] T035 [US4] Handle transaction failures gracefully
- [X] T036 [US4] Add comprehensive error handling for database connection issues
- [X] T037 [US4] Return appropriate error messages for JWT validation failures
- [X] T038 [US4] Implement proper cleanup for failed operations

## Phase 7: Testing and Validation

**Tasks**:

- [X] T039 [P] Create unit tests for Conversation model
- [X] T040 [P] Create unit tests for Message model
- [X] T041 [P] Create unit tests for conversation_service
- [X] T042 [P] Create unit tests for message_service
- [X] T043 [P] Create unit tests for auth_dependencies
- [X] T044 [P] Create contract tests for chat API using provided schema
- [X] T045 [P] Create integration tests for chat functionality
- [X] T046 Perform end-to-end testing of all user scenarios
- [X] T047 Validate all functional requirements from spec

## Phase 8: Polish & Cross-Cutting Concerns

**Tasks**:

- [X] T048 Add comprehensive logging throughout the system
- [X] T049 Implement proper error reporting and monitoring hooks
- [X] T050 Add configuration validation and startup checks
- [X] T051 Create documentation for deployment and operation
- [X] T052 Perform security review of authentication flows
- [X] T053 Optimize database queries and indexing
- [X] T054 Final integration testing and validation