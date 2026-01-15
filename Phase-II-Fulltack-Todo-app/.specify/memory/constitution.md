<!-- SYNC IMPACT REPORT
Version change: 1.0.0 → 1.1.0
Modified principles:
- Spec-Driven Accuracy: Added
- Agentic Autonomy: Added
- User Isolation: Added
- Security Rigor: Added

Added sections: Technical Standards, Agent Roles & Constraints, Success Criteria
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending
- .specify/templates/spec-template.md: ⚠ pending
- .specify/templates/tasks-template.md: ⚠ pending
- .specify/templates/commands/*.md: ⚠ pending

Follow-up TODOs:
- Update templates to align with new principles
- Verify agent-specific guidance files reference new principles
-->
# Todo Full-Stack Web Application Constitution

## Core Principles

### Spec-Driven Accuracy
No implementation shall occur without a corresponding specification in the @specs/ directory. All features must be traceable to a written requirement.

### Agentic Autonomy
All development tasks are to be performed by Claude Code acting as specialized agents. Manual coding is strictly prohibited.

### User Isolation
Privacy is a non-negotiable requirement. The system must enforce strict data partitioning so that users can only access their own data via user_id filtering.

### Security Rigor
All communication between the Frontend and Backend must be secured via Stateless JWT (JSON Web Tokens).

## Technical Standards
Frontend Stack: Next.js 16+ (App Router), TypeScript, and Tailwind CSS.

Backend Stack: Python FastAPI with SQLModel (ORM).

Database: Neon Serverless PostgreSQL (Persistent Storage).

Authentication: Better Auth (Frontend) integrated with custom JWT verification middleware (Backend).

Secret Management: A shared BETTER_AUTH_SECRET must be used by both layers for signing and verifying tokens.

## Agent Roles & Constraints
spec-specialist: Responsible for maintaining the "Single Source of Truth." Must verify that all markdown files in /specs align with Phase II requirements before triggering other agents.

backend-engineer: Responsible for the /backend scope. Must ensure the Neon DB connection is robust and all REST API endpoints are validated via Pydantic.

frontend-engineer: Responsible for the /frontend scope. Must build responsive, high-performance UI components that provide clear visual feedback (loading/success/error).

integration-specialist: The bridge between stacks. Responsible for the JWT handshake, Better Auth configuration, and the centralized api.ts client.

## Success Criteria
Stateless Authentication: Every API request must be validated using a JWT in the Authorization: Bearer <token> header. Unauthorized requests must return a 401 status.

Persistence: All task CRUD operations must reflect in the Neon PostgreSQL database.

User Ownership: Ownership must be enforced on every operation (Create, Read, Update, Delete). One user cannot modify or view another's tasks.

Zero Plagiarism/Manual Code: 100% of the codebase must be generated through agentic prompts and iteration.

## Governance
Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan. All PRs/reviews must verify compliance with these principles.

**Version**: 1.1.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07