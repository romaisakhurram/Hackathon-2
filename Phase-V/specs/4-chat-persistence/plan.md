# Implementation Plan: Chat API & Persistence

**Branch**: `4-chat-persistence` | **Date**: 2026-01-22 | **Spec**: [link to spec-4a-chat-persistence.md](./spec-4a-chat-persistence.md)

**Input**: Feature specification from `/specs/[4-chat-persistence]/spec-4a-chat-persistence.md`

## Summary

Implementation of a stateless chat API that persists conversations to the database for continuity after service restarts. The system will store all conversation messages in the database while maintaining a stateless server architecture. The API will enforce JWT-based authentication and user isolation, ensuring users can only access their own conversations. The implementation integrates with the existing AI agent and MCP tools for processing user messages.

## Technical Context

**Language/Version**: Python 3.11, Node.js 18+
**Primary Dependencies**: FastAPI, SQLModel, Neon PostgreSQL, Better Auth with JWT, OpenAI SDK (via OpenRouter)
**Storage**: Neon PostgreSQL (via existing backend)
**Testing**: pytest for backend components
**Target Platform**: Linux server (stateless)
**Project Type**: Web application (extension of existing backend)
**Performance Goals**: All chat messages persist successfully, API response times under 5 seconds, 95% of requests processed successfully
**Constraints**: <5s API response times, stateless operation, no server-side session memory, all messages stored in DB
**Scale/Scope**: Individual user isolation, supporting concurrent users with rate limiting

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-Driven Accuracy: Implementation follows spec-4a-chat-persistence.md requirements
- ✅ Agentic Autonomy: All development through Claude Code specialized agents
- ✅ User Isolation: JWT validation ensures users can only access their own conversations
- ✅ Security Rigor: JWT tokens used for authentication in all requests
- ✅ AI Provider Compliance: Using OpenRouter with OpenAI-compatible mode
- ✅ MCP Tool Integration: All task actions go through MCP tools as implemented in Spec 3A
- ✅ Natural Language Processing: AI agent processes user messages as implemented in Spec 3A

## Project Structure

### Documentation (this feature)

```text
specs/4-chat-persistence/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (extension of existing backend)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py          # Conversation model with user_id, timestamps
│   │   └── message.py               # Message model with conversation_id, user_id, role, content, timestamps
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversation_service.py  # Conversation creation, loading, validation
│   │   └── message_service.py       # Message persistence, retrieval, atomic operations
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat_router.py           # POST /api/{user_id}/chat endpoint implementation
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── rate_limiter.py          # Per-user rate limiting middleware
│   └── dependencies/
│       ├── __init__.py
│       └── auth_dependencies.py     # JWT validation and user_id extraction
└── tests/
    ├── unit/
    │   ├── models/
    │   ├── services/
    │   └── api/
    ├── integration/
    │   └── chat_integration_test.py
    └── contract/
        └── chat_api_contract_test.py
```

**Structure Decision**: Extending the existing backend structure with new models, services, and API endpoints for chat persistence. The implementation maintains the stateless architecture by loading conversation context from the database for each request rather than storing it in server memory. Rate limiting is implemented as middleware to enforce per-user request limits.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [No violations identified] | [All constitution checks passed] |