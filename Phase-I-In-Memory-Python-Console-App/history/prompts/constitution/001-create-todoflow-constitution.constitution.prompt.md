---
id: "001"
title: "Create TodoFlow Constitution"
stage: "constitution"
date: "2026-01-01"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "human"
command: "/sp.constitution"
labels: [constitution,architecture,governance]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - ".specify/memory/constitution.md"
tests:
  - "none"
---

## Prompt

/sp.constitution

Project: TodoFlow — Multi-Phase AI-Native Todo Application

Goal:
Build a todo management system that starts as a simple in-memory console application
and evolves step by step into a cloud-native, AI-assisted distributed platform.
Each phase must remain compatible with future phases without rewrites.

--------------------------------------------------
GLOBAL PRINCIPLES
--------------------------------------------------
- Correctness before scale
- Simplicity before abstraction
- Clear separation of concerns
- Deterministic, testable behavior
- Explicit errors and state
- No hidden shortcuts or magic

--------------------------------------------------
PHASE I: In-Memory Python Console Todo App
--------------------------------------------------
- Python, CLI only
- In-memory todo state
- No database, no files, no AI
- Explicit domain model (Todo, Status, Priority)
- Clean separation: domain, application, CLI
Success: Correct todo logic and clean foundation

--------------------------------------------------
PHASE II: Full-Stack Web Todo App
--------------------------------------------------
- Next.js frontend
- FastAPI backend
- SQLModel + Neon DB
- Reuse Phase I domain logic
- Stateless backend, persistent storage
Success: Reliable web UI and API for todos

--------------------------------------------------
PHASE III: AI-Powered Todo Chat Assistant
--------------------------------------------------
- OpenAI ChatKit
- Agents SDK
- Official MCP SDK
- AI assists with intent parsing and suggestions
- AI never bypasses todo business rules
- Tool calls strictly validated
Success: Predictable, controlled AI interactions

--------------------------------------------------
PHASE IV: Local Kubernetes Deployment
--------------------------------------------------
- Docker, Minikube, Helm
- One service per container
- Configuration via environment variables
- Local cluster mirrors production layout
Success: Fully reproducible local deployment

--------------------------------------------------
PHASE V: Cloud-Native Todo Platform
--------------------------------------------------
- Kafka for events
- Dapr for service communication
- DigitalOcean DOKS
- Event-driven updates and notifications
- Fault tolerance and observability required
Success: Scalable, resilient todo platform

--------------------------------------------------
CROSS-PHASE RULES
--------------------------------------------------
- No phase may block future evolution
- Refactor only with clear justification
- Each phase documents:
  - design decisions
  - trade-offs
  - migration notes

--------------------------------------------------
FINAL SUCCESS
--------------------------------------------------
- Todo logic remains correct across all phases
- Architecture evolves without rewrites
- AI remains controlled and observable
- System is production-grade by Phase V

## Response snapshot

Created TodoFlow Constitution at `.specify/memory/constitution.md` with:
- 6 core principles (Correctness Before Scale, Simplicity Before Abstraction, Clear Separation of Concerns, Deterministic/Testable Behavior, Explicit Errors/State, No Hidden Shortcuts)
- Phase-specific requirements for all 5 phases
- Cross-phase rules and final success criteria
- Governance section with amendment procedures and version policy
- Initial version: 1.0.0

## Outcome

- ✅ Impact: Project constitution established as authoritative source for all development decisions
- 🧪 Tests: N/A - governance document
- 📁 Files: `.specify/memory/constitution.md` (updated from template)
- 🔁 Next prompts: `/sp.specify` to create first feature spec, or `/sp.plan` for Phase I planning
- 🧠 Reflection: Constitution provides clear guardrails for all 5 phases while maintaining flexibility for implementation decisions. Templates validated for alignment.

## Evaluation notes (flywheel)

- Failure modes observed: "none"
- Graders run and results (PASS/FAIL): "N/A"
- Prompt variant (if applicable): "none"
- Next experiment (smallest change to try): "none"
