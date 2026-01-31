# Research: AI Agent + MCP Integration

## Decision: MCP SDK Implementation Approach
**Rationale**: Using the Official MCP SDK as specified in the constitution and spec to ensure standardization and compatibility with the broader MCP ecosystem. This acts as an integration layer between the AI agent and existing backend.
**Alternatives considered**: Custom tool implementation, direct API calls - rejected in favor of standardized MCP approach.

## Decision: OpenRouter Configuration
**Rationale**: Following constitutional requirement to use OpenRouter instead of paid OpenAI keys for cost management and compliance.
**Alternatives considered**: Direct OpenAI API, other LLM providers - OpenRouter provides OpenAI-compatible interface as required.

## Decision: Authentication Flow
**Rationale**: Leveraging existing Better Auth JWT infrastructure to maintain consistency with Phase II backend and ensure user isolation. The MCP tools will pass through the existing authentication tokens using Authorization: Bearer header format.
**Alternatives considered**: Separate AI authentication system - rejected to maintain unified auth approach.

## Decision: Backend Integration Pattern
**Rationale**: Creating an integration layer that calls into the existing Phase II backend APIs rather than duplicating functionality. MCP tools will act as adapters to the existing backend.
**Alternatives considered**: Building new backend services - rejected to leverage existing investment.

## Decision: API Endpoint Mapping
**Rationale**: Mapping MCP tools to existing backend endpoints: add_task → POST /api/tasks/, list_tasks → GET /api/tasks/, update_task → PUT /api/tasks/{id}, complete_task → PATCH /api/tasks/{id}/toggle, delete_task → DELETE /api/tasks/{id}. This leverages the existing, tested backend functionality.
**Alternatives considered**: Creating new API endpoints - rejected to maintain consistency with existing system.

## Decision: Priority Value Conversion
**Rationale**: Converting between string representations (low/medium/high) used in the UI and integer values (1/2/3) used in the backend. This ensures compatibility between the frontend, AI agent, and backend systems.
**Alternatives considered**: Changing the backend schema - rejected to maintain compatibility with existing frontend.

## Decision: State Management Strategy
**Rationale**: Implementing stateless operation as required by technical constraints, with conversation context managed through token window.
**Alternatives considered**: Server-side session storage - rejected to maintain statelessness.

## Decision: Error Handling Approach
**Rationale**: Abstract error messages to users as specified in clarifications, with detailed logging for debugging. Errors from the existing backend will be wrapped appropriately.
**Alternatives considered**: Technical error details to users - rejected for better UX and security.

## Decision: Tool Timeout Configuration
**Rationale**: 30-second timeouts as specified in clarifications to balance responsiveness with operation completion. This includes time for the existing backend to respond.
**Alternatives considered**: Shorter/longer timeouts - 30s provides good balance per spec.

## Decision: Conversation Context Window
**Rationale**: 5-10 turn context window as specified in clarifications to maintain conversation coherence without excessive resource usage.
**Alternatives considered**: Larger/smaller windows - 5-10 turns provides good balance per spec.