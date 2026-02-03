---
id: 3
title: Create frontend ui auth spec
stage: spec
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 1-frontend-ui-auth
branch: 1-frontend-ui-auth
user: unknown
command: manual
labels: ["spec", "frontend", "authentication", "ui"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-frontend-ui-auth/spec.md
 - specs/1-frontend-ui-auth/checklists/requirements.md
tests:
 - none
---

## Prompt

🚀 Frontend Agent Master Prompt: Professional UI & Auth Integration
Role: frontend-engineer & integration-specialist

Standard: sp.constitution (Professional Grade UI/UX)

References: @specs/ui/, @specs/features/authentication.md, @.claud.md/frontend/skills.md

Task: "As the frontend-engineer, your goal is to build a high-performance, aesthetically superior Todo Web Application. The UI must ally appealing 'No tasks found' illustration or message.

Add Task: A sleek input field or modal with priority selection.

Feedback: Use 'sonner' or 'react-hot-toast' for elegant success/error notifications.

Constraint: Follow the Agentic Dev Stack workflow. Read the specs first, generate a plan, and implement without manual code. Ensure responsiveness for mobile, tablet, and desktop."

What this prompt achieves:
Professionalism: It forces Claude to move beyond "basic" HTML/CSS and use modern design patterns.

Stateless Auth: It specifically mentions the JWT plugin for Better Auth, which is the most common pitfall in Phase II.

Clean Code: It organizes the API calls into a single library (/lib/api.ts) for easier debugging.

## Response snapshot

Successfully created a comprehensive specification for the Professional UI & Auth Integration feature, covering user authentication, task management, responsive design, and user experience requirements.

## Outcome

- ✅ Impact: Created complete spec for frontend UI and auth integration
- 🧪 Tests: none
- 📁 Files: 2 files created (spec.md, requirements.md)
- 🔁 Next prompts: Proceed to planning phase with /sp.plan
- 🧠 Reflection: Clear user stories and acceptance criteria defined

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A