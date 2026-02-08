# Implementation Plan: AI Agent + MCP Integration

**Branch**: `3-ai-agent-mcp` | **Date**: 2026-01-20 | **Spec**: [link to spec-3a-agent-mcp.md](./spec-3a-agent-mcp.md)

**Input**: Feature specification from `/specs/[3-ai-agent-mcp]/spec-3a-agent-mcp.md`

## Summary

Implementation of an AI agent that interprets natural language from users and uses MCP tools to manage todos through the existing backend APIs. The solution will use OpenRouter for AI capabilities and implement an MCP server that exposes standardized tools for task operations (add, list, update, complete, delete) with proper user ownership validation. The AI agent integrates with the existing Phase II frontend and backend systems.

## Technical Context

**Language/Version**: Python 3.11, Node.js 18+
**Primary Dependencies**: OpenAI SDK (compatible via OpenRouter), Official MCP SDK, FastAPI, SQLModel
**Storage**: Neon PostgreSQL (via existing backend)
**Testing**: pytest for backend components
**Target Platform**: Linux server (stateless)
**Project Type**: Web application (integrating with existing backend/frontend)
**Performance Goals**: All task operations complete within 5 seconds, 95% of requests processed successfully
**Constraints**: <30s tool call timeouts, stateless operation, no direct DB access by AI agent
**Scale/Scope**: Individual user isolation, supporting concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-Driven Accuracy: Implementation follows spec-3a-agent-mcp.md requirements
- ✅ Agentic Autonomy: All development through Claude Code specialized agents
- ✅ User Isolation: MCP tools validate user ownership for all operations
- ✅ Security Rigor: JWT tokens used for authentication in all requests
- ✅ AI Provider Compliance: Using OpenRouter with OpenAI-compatible mode
- ✅ MCP Tool Integration: All task actions must go through MCP tools
- ✅ Natural Language Processing: AI agent must infer intent from user text

## Project Structure

### Documentation (this feature)

```text
specs/3-ai-agent-mcp/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (backend integration)

```text
backend/
├── src/
│   ├── ai_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                 # Main AI agent implementation
│   │   ├── intent_recognizer.py     # Natural language intent processing
│   │   └── response_formatter.py    # Natural language response generation
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py               # MCP server implementation
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── add_task.py         # add_task MCP tool - calls existing backend POST /api/tasks/
│   │   │   ├── list_tasks.py       # list_tasks MCP tool - calls existing backend GET /api/tasks/
│   │   │   ├── update_task.py      # update_task MCP tool - calls existing backend PUT /api/tasks/{id}
│   │   │   ├── complete_task.py    # complete_task MCP tool - calls existing backend PATCH /api/tasks/{id}/toggle
│   │   │   └── delete_task.py      # delete_task MCP tool - calls existing backend DELETE /api/tasks/{id}
│   │   └── validators/
│   │       ├── __init__.py
│   │       └── ownership_validator.py  # User ownership validation using JWT
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat_endpoint.py        # Chat endpoint connecting AI to MCP
│   └── config/
│       ├── __init__.py
│       └── ai_config.py            # OpenRouter configuration
└── tests/
    ├── unit/
    │   ├── ai_agent/
    │   └── mcp_server/
    ├── integration/
    │   └── chat_integration_test.py
    └── contract/
        └── mcp_tool_contracts_test.py
```

**Structure Decision**: Integrating AI agent and MCP server directly into the existing Phase II backend structure. The AI agent and MCP tools will operate within the same backend service, sharing the same authentication and database access mechanisms. This provides tighter integration while maintaining the separation of concerns between AI logic and core backend functionality. The chat interface will be integrated into the existing frontend as a new component.

**Integration Details**:
- AI agent and MCP server run within the existing backend service
- MCP tools directly access backend services/models rather than making HTTP calls to endpoints
- Authentication uses same JWT mechanism as existing system (Authorization: Bearer token)
- User isolation maintained through existing user_id filtering in backend
- Priority values converted between string (UI) and integer (backend) representations as needed
- Chat interface component will be added to existing frontend (frontend/app/chat/page.tsx)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [No violations identified] | [All constitution checks passed] |