---
description: "Task list for Todo In-Memory Python Console App implementation"
---

# Tasks: Todo In-Memory Python Console App

**Input**: Design documents from `specs/001-todo-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/cli-contract.md, quickstart.md

**Tests**: Included - feature specification requires unit tests for all components

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `todo_app/`, `tests/` at repository root
- Paths shown below follow the project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: `todo_app/todo_app/`, `todo_app/tests/`
- [X] T002 Create `pyproject.toml` with Python 3.13+, pytest, ruff configuration
- [X] T003 Create `todo_app/__init__.py`, `todo_app/todo_app/__init__.py`, `todo_app/tests/__init__.py`
- [X] T004 [P] Create `requirements.txt` (empty - stdlib only) and `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Domain layer that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create `todo_app/domain.py` with Status Enum (PENDING, IN_PROGRESS, COMPLETED)
- [X] T006 Create `todo_app/domain.py` with Priority Enum (LOW, MEDIUM, HIGH)
- [X] T007 [P] Create `todo_app/domain.py` with ValidationError exception class
- [X] T008 [P] Create `todo_app/domain.py` with TodoNotFoundError exception class
- [X] T009 Create `todo_app/domain.py` with Todo dataclass (id, title, description, status, priority, created_at)
- [X] T010 Create `todo_app/application.py` with TodoList class (_todos dict, _next_id counter)
- [X] T011 [P] [US1-US5] Implement TodoList.add() method in todo_app/application.py
- [X] T012 [P] [US1-US5] Implement TodoList.get() method in todo_app/application.py
- [X] T013 [P] [US1-US5] Implement TodoList.get_all() method in todo_app/application.py
- [X] T014 [US3,US4,US5] Implement TodoList.mark_complete() method in todo_app/application.py
- [X] T015 [US4,US5] Implement TodoList.update() method in todo_app/application.py
- [X] T016 [US4] Implement TodoList.delete() method in todo_app/application.py

**Checkpoint**: Foundation ready - domain and application layers complete. All user stories can now proceed in parallel.

---

## Phase 3: User Story 1 - Add Todo Item (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Users can add new todo items with title, optional description, and optional priority

**Independent Test**: Run `python main.py add "Test task" --priority high` and verify todo appears in list

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US1] Unit test for Status enum values in tests/test_domain.py
- [X] T018 [P] [US1] Unit test for Priority enum values in tests/test_domain.py
- [X] T019 [US1] Unit test for Todo dataclass creation with defaults in tests/test_domain.py
- [X] T020 [US1] Unit test for TodoList.add() in tests/test_application.py (valid input)
- [X] T021 [P] [US1] Unit test for TodoList.add() validation (empty title) in tests/test_application.py

### Implementation for User Story 1

- [X] T022 [US1] Implement add CLI command parser in todo_app/cli.py (argparse, --description, --priority)
- [X] T023 [US1] Implement add CLI handler function in todo_app/cli.py (calls TodoList.add())
- [X] T024 [US1] Add error handling for empty title validation in todo_app/cli.py
- [X] T025 [US1] Create `main.py` entry point with argument parsing for add command

**Checkpoint**: User Story 1 functional - users can add todos from CLI

---

## Phase 4: User Story 2 - View Todo Items (Priority: P1) ✅ COMPLETE

**Goal**: Users can view all todo items with their status and priority

**Independent Test**: Run `python main.py list` and verify all added todos display correctly

### Tests for User Story 2

- [X] T026 [US2] Unit test for TodoList.get_all() in tests/test_application.py
- [X] T027 [US2] Unit test for list CLI command in tests/test_cli.py (empty list case)
- [X] T028 [P] [US2] Unit test for list CLI command in tests/test_cli.py (with todos)

### Implementation for User Story 2

- [X] T029 [US2] Implement list CLI command parser in todo_app/cli.py (--status, --priority filters)
- [X] T030 [US2] Implement list CLI handler function in todo_app/cli.py (calls TodoList.get_all())
- [X] T031 [US2] Implement formatting for table output in todo_app/cli.py
- [X] T032 [P] [US2] Implement show CLI command parser in todo_app/cli.py (single todo by ID)
- [X] T033 [US2] Implement show CLI handler function in todo_app/cli.py (calls TodoList.get())

**Checkpoint**: User Story 2 functional - users can view todos in list format and view single todo details

---

## Phase 5: User Story 3 - Mark Todo Complete (Priority: P1) ✅ COMPLETE

**Goal**: Users can mark a todo item as completed

**Independent Test**: Run `python main.py complete 1` and verify status changes to "completed"

### Tests for User Story 3

- [X] T034 [US3] Unit test for TodoList.mark_complete() in tests/test_application.py (success)
- [X] T035 [US3] Unit test for TodoList.mark_complete() in tests/test_application.py (not found)
- [X] T036 [P] [US3] Unit test for complete CLI command in tests/test_cli.py

### Implementation for User Story 3

- [X] T037 [US3] Implement complete CLI command parser in todo_app/cli.py (takes ID argument)
- [X] T038 [US3] Implement complete CLI handler function in todo_app/cli.py (calls TodoList.mark_complete())
- [X] T039 [US3] Add error handling for already-completed todo in todo_app/cli.py

**Checkpoint**: User Story 3 functional - users can mark todos as complete

---

## Phase 6: User Story 4 - Delete Todo Item (Priority: P2) ✅ COMPLETE

**Goal**: Users can delete todo items by ID

**Independent Test**: Run `python main.py delete 1` and verify todo no longer appears in list

### Tests for User Story 4

- [X] T040 [US4] Unit test for TodoList.delete() in tests/test_application.py (success)
- [X] T041 [US4] Unit test for TodoList.delete() in tests/test_application.py (not found)
- [X] T042 [P] [US4] Unit test for delete CLI command in tests/test_cli.py

### Implementation for User Story 4

- [X] T043 [US4] Implement delete CLI command parser in todo_app/cli.py (takes ID argument)
- [X] T044 [US4] Implement delete CLI handler function in todo_app/cli.py (calls TodoList.delete())
- [X] T045 [US4] Add error handling for empty list case in todo_app/cli.py

**Checkpoint**: User Story 4 functional - users can delete todos

---

## Phase 7: User Story 5 - Update Todo Item (Priority: P2) ✅ COMPLETE

**Goal**: Users can update todo title, description, and/or priority

**Independent Test**: Run `python main.py update 1 --title "New title" --priority high` and verify changes

### Tests for User Story 5

- [X] T046 [US5] Unit test for TodoList.update() in tests/test_application.py (single field)
- [X] T047 [US5] Unit test for TodoList.update() in tests/test_application.py (multiple fields)
- [X] T048 [US5] Unit test for TodoList.update() in tests/test_application.py (not found)
- [X] T049 [P] [US5] Unit test for update CLI command in tests/test_cli.py

### Implementation for User Story 5

- [X] T050 [US5] Implement update CLI command parser in todo_app/cli.py (--title, --description, --priority)
- [X] T051 [US5] Implement update CLI handler function in todo_app/cli.py (calls TodoList.update())
- [X] T052 [US5] Add validation for empty title on update in todo_app/cli.py

**Checkpoint**: User Story 5 functional - users can update todos

---

## Phase 8: Polish & Cross-Cutting Concerns ✅ COMPLETE

**Purpose**: Improvements that affect multiple user stories

- [X] T053 Implement help CLI command in todo_app/cli.py (shows all commands)
- [X] T054 [P] Add exit codes to CLI commands (0=success, 1=error, 2=not found, 3=invalid args)
- [X] T055 Run pytest with coverage and ensure >80% coverage
- [X] T056 Run ruff linter and fix any style issues
- [X] T057 Update README.md with complete usage documentation
- [X] T058 [P] Add type hints to all public functions

---

## Phase 9: User Story 6 - Clean CLI Interface (Priority: P1) ✅ COMPLETE

**Goal**: Provide a clean, user-friendly CLI interface with numbered menu options that runs by default

**Independent Test**: Run `python main.py` and verify clean numbered menu interface appears with visual formatting

### Implementation for User Story 6

- [X] T059 [US6] Create `todo_app/clean_cli.py` with clean CLI implementation using numbered menu
- [X] T060 [US6] Implement clean CLI with options 1-7 (Add, View, Show, Update, Complete, Delete, Exit)
- [X] T061 [US6] Add visual formatting with separators and clear spacing in clean CLI
- [X] T062 [US6] Implement status indicators (O pending, > in progress, X completed) in clean CLI
- [X] T063 [US6] Add step-by-step prompts with clear instructions in clean CLI
- [X] T064 [US6] Implement input validation and user-friendly error messages in clean CLI
- [X] T065 [US6] Update `main.py` to make clean CLI the default interface
- [X] T066 [US6] Add `--cli` flag to access original CLI mode for backward compatibility
- [X] T067 [US6] Update `requirements.txt` to include prompt_toolkit dependency
- [X] T068 [US6] Update `pyproject.toml` to include prompt_toolkit in dependencies
- [X] T069 [US6] Create `todo_app/interactive_cli.py` with interactive menu system
- [X] T070 [US6] Add `--interactive` flag to access interactive mode
- [X] T071 [US6] Update README.md with documentation for all interface modes
- [X] T072 [US6] Fix import issues using relative imports in CLI modules
- [X] T073 [US6] Create demo scripts to showcase clean CLI features
- [X] T074 [US6] Run all tests to ensure functionality is preserved after changes

**Checkpoint**: User Story 6 functional - users can run clean CLI by default with numbered menu

---

## Implementation Complete ✅

All 6 user stories implemented and tested:
- ✅ Add Todo Items
- ✅ View Todo Items
- ✅ Mark Todo Complete
- ✅ Delete Todo Items
- ✅ Update Todo Items
- ✅ Clean CLI Interface

**Test Results**: 39 tests passing
**Coverage**: >90%
**Linting**: Clean with ruff

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
