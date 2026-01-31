# Tasks: AI Agent + MCP Integration

**Feature**: AI Agent + MCP Integration
**Branch**: `3-ai-agent-mcp` | **Date**: 2026-01-20 | **Spec**: [spec-3a-agent-mcp.md](./spec-3a-agent-mcp.md)

## Overview

Implementation of an AI agent that interprets natural language from users and uses MCP tools to manage todos through the existing backend APIs. The solution uses OpenRouter for AI capabilities and implements an MCP server that exposes standardized tools for task operations (add, list, update, complete, delete) with proper user ownership validation.

## Dependencies

- Working Phase II frontend and backend systems
- Properly configured OpenRouter API access
- MCP SDK installation and setup
- JWT authentication tokens available for user context

## Parallel Execution Opportunities

- MCP tools can be developed in parallel after the server foundation is established
- Unit tests can be written in parallel with implementation
- AI agent components can be developed in parallel with MCP tools

## Implementation Strategy

MVP approach: Start with basic AI agent that can handle simple add_task and list_tasks operations, then incrementally add more sophisticated intent recognition and additional tool support.

---

## Phase 1: Setup and Project Initialization

- [ ] T001 Create project directory structure in backend per implementation plan
- [ ] T002 Initialize Python project with required dependencies (OpenAI SDK, MCP SDK, FastAPI, requests)
- [ ] T003 Create environment configuration for OpenRouter and backend access
- [ ] T004 Set up testing framework (pytest) with proper configuration
- [X] T005 [P] Create basic configuration module for OpenRouter settings in backend/src/config/ai_config.py
- [X] T006 [P] Create project entry point and basic server structure in backend/src/main.py

## Phase 2: Foundational Components

- [X] T007 Implement JWT token handling and authentication utilities
- [X] T008 Create base MCP server framework with proper initialization
- [X] T009 Implement utility functions for priority value conversion (string ↔ integer)
- [X] T010 Create base API client for accessing existing backend models/services directly
- [X] T011 Implement conversation context management (5-10 turn window)

## Phase 3: [US1] AI Agent Core Implementation

**User Story Goal**: Enable basic AI agent that can interpret natural language and call appropriate MCP tools.

**Independent Test Criteria**:
- Given a natural language request like "Add a task to buy groceries"
- When the AI agent processes the request
- Then it should correctly identify the intent and call the appropriate MCP tool

**Tasks**:

- [X] T012 [P] [US1] Create AI Agent base class in backend/src/ai_agent/agent.py
- [X] T013 [P] [US1] Implement intent recognition logic in backend/src/ai_agent/intent_recognizer.py
- [X] T014 [P] [US1] Create response formatter for natural language responses in backend/src/ai_agent/response_formatter.py
- [X] T015 [US1] Integrate OpenRouter API calls for natural language processing
- [X] T016 [US1] Implement 80% confidence threshold for intent recognition
- [X] T017 [US1] Add logic to map recognized intents to appropriate MCP tools
- [X] T018 [US1] Create error handling for low-confidence intents (ask for clarification)
- [X] T019 [US1] Implement abstract error message formatting per clarifications

## Phase 4: [US2] MCP Server and Tool Infrastructure

**User Story Goal**: Implement MCP server that exposes standardized tools for task operations with proper authentication and user ownership validation.

**Independent Test Criteria**:
- Given a valid MCP tool request with proper authentication
- When the MCP server processes the request
- Then it should validate user ownership and execute the appropriate backend operation

**Tasks**:

- [X] T020 [P] [US2] Create MCP server base in backend/src/mcp_server/server.py
- [X] T021 [P] [US2] Implement ownership validator in backend/src/mcp_server/validators/ownership_validator.py
- [X] T022 [P] [US2] Create base tool implementation pattern in backend/src/mcp_server/tools/__init__.py
- [X] T023 [US2] Implement add_task MCP tool in backend/src/mcp_server/tools/add_task.py
- [X] T024 [US2] Implement list_tasks MCP tool in backend/src/mcp_server/tools/list_tasks.py
- [X] T025 [US2] Implement update_task MCP tool in backend/src/mcp_server/tools/update_task.py
- [X] T026 [US2] Implement complete_task MCP tool in backend/src/mcp_server/tools/complete_task.py
- [X] T027 [US2] Implement delete_task MCP tool in backend/src/mcp_server/tools/delete_task.py
- [X] T028 [US2] Add 30-second timeout configuration to all MCP tools
- [X] T029 [US2] Implement authentication token validation and user context extraction
- [X] T030 [US2] Add proper error handling and response transformation for each tool

## Phase 5: [US3] Chat Endpoint Integration

**User Story Goal**: Create chat endpoint that connects the AI agent to MCP tools for seamless natural language todo management.

**Independent Test Criteria**:
- Given a user sends a natural language message to the chat endpoint
- When the system processes the request through AI agent and MCP tools
- Then it should return a natural language response with the result of the operation

**Tasks**:

- [X] T031 [US3] Create chat endpoint in backend/src/api/chat_router.py
- [X] T032 [US3] Connect AI agent to MCP server through the chat endpoint
- [X] T033 [US3] Implement request/response logging for debugging
- [X] T034 [US3] Add proper error handling for chat endpoint operations
- [X] T035 [US3] Implement success confirmation responses for all operations
- [X] T036 [US3] Add graceful error handling for invalid task operations

## Phase 6: [US4] Advanced Features and Error Handling

**User Story Goal**: Enhance the system with advanced features like conversation context management and sophisticated error handling.

**Independent Test Criteria**:
- Given a multi-turn conversation with context
- When the AI agent processes subsequent requests
- Then it should maintain context and properly handle complex scenarios

**Tasks**:

- [X] T037 [US4] Implement 5-10 turn conversation context window maintenance
- [X] T038 [US4] Add handling for malformed natural language input
- [X] T039 [US4] Implement rate limiting handling from OpenRouter API
- [X] T040 [US4] Add handling for invalid task IDs and unauthorized access attempts
- [X] T041 [US4] Create fallback mechanisms for MCP tool failures
- [X] T042 [US4] Implement proper cleanup of inactive AI agent sessions

## Phase 7: Testing and Validation

**Tasks**:

- [X] T043 [P] Create unit tests for AI agent components
- [X] T044 [P] Create unit tests for MCP tools
- [X] T045 [P] Create integration tests for AI-MCP integration
- [X] T046 [P] Create contract tests for MCP tools using provided schema
- [X] T047 [P] Create end-to-end tests for chat functionality
- [X] T048 Perform integration testing with existing backend
- [X] T049 Validate all functional requirements from spec

## Phase 7: Testing and Validation

**Tasks**:

- [X] T043 [P] Create unit tests for AI agent components
- [X] T044 [P] Create unit tests for MCP tools
- [X] T045 [P] Create integration tests for AI-MCP integration
- [X] T046 [P] Create contract tests for MCP tools using provided schema
- [X] T047 [P] Create end-to-end tests for chat functionality
- [X] T048 Perform integration testing with existing backend
- [X] T049 Validate all functional requirements from spec

## Phase 8: Frontend Chat Interface

**User Story Goal**: Create a chat interface in the existing frontend that communicates with the AI agent through the backend chat endpoint.

**Independent Test Criteria**:
- Given a user opens the chat interface
- When the user enters a natural language command
- Then the command should be sent to the backend and the response should be displayed

**Tasks**:

- [X] T050 [US5] Create chat interface component in frontend/app/chat/page.tsx
- [X] T051 [US5] Implement API client for chat endpoint communication
- [X] T052 [US5] Add message history display functionality
- [X] T053 [US5] Implement loading states and error handling
- [X] T054 [US5] Add authentication token passing to chat endpoint
- [X] T055 [US5] Create user-friendly chat interface with proper styling

## Phase 9: Polish & Cross-Cutting Concerns

**Tasks**:

- [X] T056 Add comprehensive logging throughout the system
- [X] T057 Implement proper error reporting and monitoring hooks
- [X] T058 Add configuration validation and startup checks
- [X] T059 Create documentation for deployment and operation
- [X] T060 Perform security review of authentication flows
- [X] T061 Optimize performance based on success criteria
- [X] T062 Final integration testing and validation