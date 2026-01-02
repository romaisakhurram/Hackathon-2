# Implementation Plan: Todo In-Memory Python Console App

**Branch**: `001-todo-console-app` | **Date**: 2026-01-01 | **Spec**: `specs/001-todo-console-app/spec.md`
**Input**: Feature specification from `/specs/001-todo-console-app/spec.md`

## Summary

Build a command-line todo application with in-memory storage implementing Add, Delete, Update, View, and Mark Complete features. The application follows clean architecture with three distinct layers: domain (Todo entity and rules), application (use cases and state management), and CLI (user interface). Python 3.13+ is the target language with no external dependencies, files, databases, or AI calls.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only)
**Storage**: In-memory (dict/list), no persistence
**Testing**: pytest (unit tests)
**Target Platform**: Console/terminal (cross-platform Python)
**Project Type**: Single project (CLI application)
**Performance Goals**: N/A (single-user CLI, instant responses expected)
**Constraints**: CLI only, no files/db/AI, deterministic behavior, no global mutable state
**Scale/Scope**: Single user, minimal scope (5 core features)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Correctness Before Scale | ✅ PASS | In-memory design prioritizes correctness; simple architecture minimizes bugs |
| II. Simplicity Before Abstraction | ✅ PASS | No unnecessary layers; standard library only; explicit data structures |
| III. Clear Separation of Concerns | ✅ PASS | Three-layer architecture (domain/application/CLI) explicitly required |
| IV. Deterministic, Testable Behavior | ✅ PASS | In-memory state is fully observable; no external dependencies |
| V. Explicit Errors and State | ✅ PASS | Custom exceptions and Result types for all operations |
| VI. No Hidden Shortcuts or Magic | ✅ PASS | No globals; explicit initialization; no implicit behavior |

**Result**: All gates pass. No complexity tracking required.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-console-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (skipped - no clarifications needed)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-contract.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
todo_app/
├── todo_app/
│   ├── __init__.py
│   ├── domain.py        # Todo entity, enums, domain exceptions
│   ├── application.py   # TodoList service, use case functions
│   ├── cli.py           # Original CLI interface, menus, input handling
│   ├── clean_cli.py     # Clean CLI interface with numbered menu
│   └── interactive_cli.py # Interactive CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_domain.py   # Todo entity tests
│   ├── test_application.py  # TodoList service tests
│   └── test_cli.py      # CLI integration tests
├── main.py              # Entry point with multiple interface modes
├── pyproject.toml       # Project configuration
├── requirements.txt     # Dependencies including prompt_toolkit
└── README.md            # User-facing documentation
```

**Structure Decision**: Using `todo_app/` as the package directory with `__init__.py` files for proper Python packaging. Tests mirror the source structure for clarity. `pyproject.toml` for modern Python project configuration.

## Design Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| dataclasses for Todo | Reduces boilerplate, built-in type hints support, automatic `__repr__` | NamedTuple (less flexible), attrs (external dep) |
| Enum for Status/Priority | Type safety, prevents invalid values | String literals (prone to typos), custom class |
| Custom exceptions | Explicit error handling per constitution | Generic exceptions (less clear) |
| No global state | Testability, reusability, follows constitution | Module-level list (hidden state) |
| Click for CLI? No - use argparse | argparse is stdlib, no dependencies | Click (external), typer (external) |
| Clean CLI as default | Improves user experience with intuitive numbered menu | Keep original CLI as default |
| Relative imports | Proper module resolution in nested package structure | Absolute imports causing import errors |
| Multiple interface modes | Supports different user preferences (clean CLI, interactive, original CLI) | Single interface approach |

## Complexity Tracking

> Not applicable - all gates pass with no violations requiring justification.
