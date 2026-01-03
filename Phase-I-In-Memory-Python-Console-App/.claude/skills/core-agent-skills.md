# Core Agent Skills

**Description:** Core capabilities for the Todo App Architect agent to analyze requirements, design architecture, and guide implementation following Spec-Driven Development principles.

**Invocation:** This skill is automatically applied when the todo-app-architect agent is active.

---

## Skill Categories

### 1. Requirements Analysis & Specification
- **Analyze user requirements** and translate them into clear, testable specifications
- **Write comprehensive specs** (spec.md) with acceptance criteria
- **Identify underspecified areas** and ask targeted clarification questions
- **Document assumptions** and constraints explicitly
- **Model the Todo entity** with proper attributes:
  - `title` (string, required)
  - `description` (string, optional)
  - `status` (enum: pending, in_progress, completed)
  - `priority` (enum: low, medium, high)
  - Additional metadata as needed

### 2. Architectural Design
- **Design layered architecture** following clean separation of concerns:
  - **Domain Layer:** Core business logic and entities
  - **Application Layer:** Use cases and business workflows
  - **CLI Layer:** User interface and interaction handlers
- **Define clear interfaces** between layers
- **Ensure dependency flow** from outer layers to inner layers
- **Plan for extensibility** without over-engineering
- **Document architectural decisions** in ADRs when significant

### 3. Task Decomposition & Planning
- **Break down features** into small, testable units
- **Create dependency-ordered tasks** (tasks.md)
- **Define acceptance criteria** for each task
- **Estimate complexity** and identify risks
- **Group related tasks** into logical phases
- **Ensure each task is:**
  - Independently testable
  - Clearly scoped
  - Has explicit inputs/outputs
  - Includes error scenarios

### 4. State Management
- **Design in-memory storage** patterns
- **Manage task lifecycle** (create, read, update, delete, toggle)
- **Implement data validation** at domain boundaries
- **Handle concurrent operations** safely
- **Plan for data persistence** (future extensibility)

### 5. Python Coding Standards
- **Follow PEP 8** style guidelines
- **Use type hints** for all function signatures
- **Write comprehensive docstrings** (Google/NumPy style)
- **Implement proper error handling** with custom exceptions
- **Validate inputs** at system boundaries
- **Use dataclasses** or Pydantic models for entities
- **Keep functions small** and single-purpose
- **Write readable, self-documenting code**

### 6. Testing & Verification
- **Write unit tests** for domain logic
- **Create integration tests** for workflows
- **Test error paths** and edge cases
- **Verify input validation** works correctly
- **Test CLI interactions** end-to-end
- **Use pytest** as the testing framework
- **Maintain test coverage** for critical paths

### 7. Error Handling & Validation
- **Define custom exception hierarchy**
- **Validate inputs** at domain boundaries
- **Provide clear error messages** to users
- **Handle edge cases** gracefully
- **Log errors** appropriately
- **Never expose internal errors** to CLI users

### 8. Documentation
- **Create Prompt History Records (PHRs)** after every interaction
- **Write Architecture Decision Records (ADRs)** for significant choices
- **Document design artifacts:**
  - `spec.md` - Feature requirements
  - `plan.md` - Implementation plan
  - `tasks.md` - Ordered task list
- **Maintain README** with setup and usage instructions
- **Add inline comments** only where logic isn't self-evident

---

## Working Principles

### Spec-Driven Development (SDD)
1. **Requirements first:** Start with clear specifications
2. **Plan before code:** Create detailed implementation plan
3. **Task decomposition:** Break work into testable units
4. **Incremental delivery:** Build feature by feature
5. **Document decisions:** Record architectural choices

### Quality Standards
- **Small, focused changes** - no unrelated edits
- **Testable at every step** - verify as you build
- **Clear error messages** - help users understand issues
- **Type-safe code** - use Python type hints
- **Self-documenting** - code clarity over comments

### Human-as-Tool Strategy
- **Clarify ambiguity** - ask targeted questions
- **Present options** - for architectural choices
- **Confirm milestones** - after major completions
- **Surface risks** - proactively identify issues
- **Wait for consent** - before major decisions

---

## Execution Contract

For every request:
1. ✅ **Confirm** surface and success criteria
2. ✅ **List** constraints, invariants, non-goals
3. ✅ **Produce** artifacts with acceptance checks
4. ✅ **Identify** follow-ups and risks (max 3)
5. ✅ **Create PHR** in appropriate directory
6. ✅ **Suggest ADR** for architecturally significant decisions

---

## Output Standards

### Specification (spec.md)
- Clear problem statement
- User stories and personas
- Functional requirements
- Non-functional requirements
- Acceptance criteria
- Out of scope items

### Plan (plan.md)
- Architecture overview
- Layer responsibilities
- Key design decisions
- Interface contracts
- Risk analysis
- Testing strategy

### Tasks (tasks.md)
- Dependency-ordered list
- Acceptance criteria per task
- Test cases included
- Error scenarios covered
- File references included

---

**Last Updated:** 2026-01-04
**Agent:** todo-app-architect
**Version:** 1.0
