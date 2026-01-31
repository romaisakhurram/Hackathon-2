---
id: 2
title: Update project constitution for todo app
stage: constitution
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-app
branch: main
user: unknown
command: manual
labels: ["constitution", "governance", "todo-app", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Project: Todo Full-Stack Web Application (Phase II)

Framework: Agentic Dev Stack (Spec-Driven Development)

Core Objective: Transforming a console application into a secure, multi-user web application with persistent storage and JWT-based authentication.

🏛️ Core Principles
Spec-Driven Accuracy: No implementation shall occur without a corresponding specification in the @specs/ directory. All features must be traceable to a written requirement.

Agentic Autonomy: All development tasks are to be performed by Claude Code acting as specialized agents. Manual coding is strictly prohibited.

User Isolation: Privacy is a non-negotiable requirement. The system must enforce strict data partitioning so that users can only access their own data via user_id filtering.

Security Rigor: All communication between the Frontend and Backend must be secured via Stateless JWT (JSON Web Tokens).

🛠️ Technical Standards
Frontend Stack: Next.js 16+ (App Router), TypeScript, and Tailwind CSS.

Backend Stack: Python FastAPI with SQLModel (ORM).

Database: Neon Serverless PostgreSQL (Persistent Storage).

Authentication: Better Auth (Frontend) integrated with custom JWT verification middleware (Backend).

Secret Management: A shared BETTER_AUTH_SECRET must be used by both layers for signing and verifying tokens.

🤖 Agent Roles & Constraints
spec-specialist: Responsible for maintaining the "Single Source of Truth." Must verify that all markdown files in /specs align with Phase II requirements before triggering other agents.

backend-engineer: Responsible for the /backend scope. Must ensure the Neon DB connection is robust and all REST API endpoints are validated via Pydantic.

frontend-engineer: Responsible for the /frontend scope. Must build responsive, high-performance UI components that provide clear visual feedback (loading/success/error).

integration-specialist: The bridge between stacks. Responsible for the JWT handshake, Better Auth configuration, and the centralized api.ts client.

✅ Success Criteria
Stateless Authentication: Every API request must be validated using a JWT in the Authorization: Bearer <token> header. Unauthorized requests must return a 401 status.

Persistence: All task CRUD operations must reflect in the Neon PostgreSQL database.

User Ownership: Ownership must be enforced on every operation (Create, Read, Update, Delete). One user cannot modify or view another's tasks.

Zero Plagiarism/Manual Code: 100% of the codebase must be generated through agentic prompts and iteration.

## Response snapshot

Successfully updated the project constitution with the new principles and standards for the Todo Full-Stack Web Application, including Spec-Driven Accuracy, Agentic Autonomy, User Isolation, and Security Rigor principles.

## Outcome

- ✅ Impact: Updated constitution with comprehensive principles for todo app development
- 🧪 Tests: none
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Implement features following the new constitution guidelines
- 🧠 Reflection: Clear governance structure established for agentic development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A