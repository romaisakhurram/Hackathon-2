<!-- SYNC IMPACT REPORT
Version change: 1.1.0 → 1.2.0
Modified principles:
- Spec-Driven Accuracy: Updated to reflect AI chatbot context
- Agentic Autonomy: Updated to reflect AI chatbot context
- User Isolation: Updated to reflect AI chatbot context
- Security Rigor: Updated to reflect AI chatbot context
- AI Provider Compliance: Added
- Natural Language Processing: Added
- MCP Tool Integration: Added

Added sections: AI Provider Policy, Agent Behavior Guidelines, Chat Flow Architecture
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending
- .specify/templates/spec-template.md: ⚠ pending
- .specify/templates/tasks-template.md: ⚠ pending
- .specify/templates/commands/*.md: ⚠ pending

Follow-up TODOs:
- Update templates to align with new AI-specific principles
- Verify agent-specific guidance files reference new AI principles
-->
# Todo AI Chatbot Constitution (Phase III)

## Core Principles

### Spec-Driven Accuracy
No implementation shall occur without a corresponding specification in the @specs/ directory. All features must be traceable to a written requirement, particularly for AI intent interpretation and natural language processing.

### Agentic Autonomy
All development tasks are to be performed by Claude Code acting as specialized agents. Manual coding is strictly prohibited. AI must operate through defined MCP tools rather than direct implementation.

### User Isolation
Privacy is a non-negotiable requirement. The system must enforce strict data partitioning so that users can only access their own data via user_id filtering, with AI respecting these boundaries.

### Security Rigor
All communication between the Frontend, Backend, and AI provider must be secured via Stateless JWT (JSON Web Tokens) and secure API key management.

### AI Provider Compliance
AI interactions must exclusively use OpenRouter with OpenAI-compatible mode. No direct access to paid OpenAI keys is permitted. Environment variables must include OPENAI_API_KEY, OPENAI_BASE_URL=https://openrouter.ai/api/v1, and configurable OPENAI_MODEL.

### Natural Language Processing
The AI must infer intent from user text inputs and translate them into appropriate MCP tool calls. Ambiguous requests should be clarified rather than assumed.

### MCP Tool Integration
All task actions must be executed through MCP tools, with proper validation of task ownership and fixed schemas. The AI serves as an orchestrator, not a direct database accessor.

## Technical Standards
Frontend Stack: Next.js 16+ (App Router), TypeScript, and Tailwind CSS.

Backend Stack: Python FastAPI with SQLModel (ORM).

Database: Neon Serverless PostgreSQL (Persistent Storage).

Authentication: Better Auth (Frontend) integrated with custom JWT verification middleware (Backend).

AI Provider: OpenRouter with OpenAI-compatible API.

Secret Management: A shared BETTER_AUTH_SECRET must be used by both layers for signing and verifying tokens, with separate AI API key management.

## Agent Roles & Constraints
spec-specialist: Responsible for maintaining the "Single Source of Truth." Must verify that all markdown files in /specs align with Phase III AI chatbot requirements before triggering other agents.

backend-engineer: Responsible for the /backend scope. Must ensure the Neon DB connection is robust and all REST API endpoints are validated via Pydantic, with proper AI integration hooks.

frontend-engineer: Responsible for the /frontend scope. Must build responsive, high-performance UI components that provide clear visual feedback (loading/success/error) for AI interactions.

integration-specialist: The bridge between stacks. Responsible for the JWT handshake, Better Auth configuration, centralized api.ts client, and AI service integration.

ai-engineer: Responsible for AI orchestration and intent recognition. Must ensure all user requests are properly interpreted and routed to appropriate MCP tools.

## AI Provider Policy
- Use OpenRouter only
- OpenAI-compatible mode required
- No paid OpenAI keys
- Required env: OPENAI_API_KEY (OpenRouter), OPENAI_BASE_URL=https://openrouter.ai/api/v1, OPENAI_MODEL (configurable)

## Agent Behavior Guidelines
- Infer intent from user text
- Use MCP tools for all actions
- Confirm every successful action
- Handle errors gracefully

## Chat Flow Architecture
1. Receive message from user
2. Load user context and authentication
3. Parse intent from natural language input
4. Validate user permissions for requested action
5. Execute appropriate MCP tool(s)
6. Format and return response to user

## Success Criteria
Stateless Authentication: Every API request must be validated using a JWT in the Authorization: Bearer <token> header. Unauthorized requests must return a 401 status.

AI Intent Recognition: The AI must correctly interpret natural language commands and map them to appropriate MCP tool calls.

Persistence: All task CRUD operations must reflect in the Neon PostgreSQL database via MCP tools.

User Ownership: Ownership must be enforced on every operation (Create, Read, Update, Delete). One user cannot modify or view another's tasks.

Zero Plagiarism/Manual Code: 100% of the codebase must be generated through agentic prompts and iteration.

AI Safety: All AI responses must be filtered to prevent inappropriate actions or data access violations.

## Governance
Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan. All PRs/reviews must verify compliance with these principles.

**Version**: 1.2.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20