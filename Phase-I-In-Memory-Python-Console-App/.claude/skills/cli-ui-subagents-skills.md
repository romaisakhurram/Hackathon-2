# CLI UI Subagents Skills

**Description:** Specialized skills for CLI UI subagents that handle interactive user workflows for task management operations.

**Invocation:** These skills are automatically applied when CLI UI subagents (cli-add-task, task-deleter, task-updater, cli-task-viewer, cli-task-toggler) are active.

---

## Subagent-Specific Skills

### 1. Add Task (cli-add-task)
**Purpose:** Guide users through creating new tasks with proper validation and confirmation.

#### Core Capabilities:
- **Interactive Input Prompts:**
  - Prompt for task title (required)
  - Prompt for description (optional)
  - Prompt for priority (low/medium/high)
  - Use clear, user-friendly language
  - Show examples when helpful

- **Input Validation:**
  - Ensure title is non-empty and reasonable length
  - Validate priority is valid enum value
  - Sanitize inputs for safety
  - Provide helpful error messages on invalid input
  - Re-prompt until valid input received

- **In-Memory Task Creation:**
  - Call domain layer to create task
  - Generate unique task ID
  - Set default status to 'pending'
  - Timestamp creation time

- **User Confirmation:**
  - Display created task details
  - Show task ID for reference
  - Confirm successful creation
  - Provide next action suggestions

#### Error Scenarios:
- Handle duplicate task detection
- Manage creation failures gracefully
- Validate against business rules
- Provide actionable error messages

---

### 2. Delete Task (task-deleter)
**Purpose:** Safely remove tasks with user confirmation to prevent accidental deletions.

#### Core Capabilities:
- **List Available Tasks:**
  - Display all tasks with IDs
  - Show task details (title, status, priority)
  - Format output for readability
  - Handle empty task list gracefully

- **Task Selection:**
  - Prompt for task ID to delete
  - Validate ID exists
  - Show selected task details
  - Allow cancellation

- **Confirmation Workflow:**
  - Ask for explicit confirmation (Y/N)
  - Show what will be deleted
  - Warn about permanent deletion
  - Allow user to abort

- **Remove Task:**
  - Call domain layer delete method
  - Remove from in-memory storage
  - Handle deletion errors

- **Deletion Confirmation:**
  - Confirm successful deletion
  - Show updated task count
  - Suggest next actions

#### Error Scenarios:
- Task ID not found
- Task already deleted
- Deletion constraints violated
- User cancellation handling

---

### 3. Update Task (task-updater)
**Purpose:** Modify existing task properties with validation and clear feedback.

#### Core Capabilities:
- **Task Selection:**
  - List available tasks
  - Prompt for task ID to update
  - Validate task exists
  - Display current task details

- **Field Selection:**
  - Show updatable fields (title, description, priority, status)
  - Prompt which field(s) to update
  - Show current values
  - Allow multiple field updates

- **Input Validation:**
  - Validate new values for each field
  - Ensure status transitions are valid
  - Check priority values
  - Validate title non-empty

- **Apply Updates:**
  - Call domain layer update method
  - Apply changes atomically
  - Handle partial update failures
  - Maintain data integrity

- **Update Feedback:**
  - Show before/after comparison
  - Confirm successful update
  - Display updated task details
  - Suggest related actions

#### Error Scenarios:
- Task not found
- Invalid field values
- Illegal status transitions
- Update conflicts

---

### 4. View Tasks (cli-task-viewer)
**Purpose:** Display tasks with filtering, sorting, and readable formatting.

#### Core Capabilities:
- **Display All Tasks:**
  - Show task list in table/list format
  - Include ID, title, status, priority
  - Use colors/formatting for clarity
  - Handle empty list gracefully

- **Filtering Options:**
  - Filter by status (pending/in_progress/completed)
  - Filter by priority (low/medium/high)
  - Combine multiple filters
  - Show filter summary

- **Sorting Options:**
  - Sort by priority (high to low)
  - Sort by status
  - Sort by creation date
  - Sort by title alphabetically

- **Readable Output:**
  - Use clear column headers
  - Align columns properly
  - Truncate long descriptions
  - Show task count summary
  - Use visual separators

- **Detail View:**
  - Show full task details on request
  - Include all metadata
  - Display creation/update timestamps
  - Format multiline descriptions

#### Error Scenarios:
- No tasks found
- Invalid filter/sort options
- Display formatting issues

---

### 5. Mark Complete (cli-task-toggler)
**Purpose:** Toggle task completion status with validation and confirmation.

#### Core Capabilities:
- **Status Toggle:**
  - Switch between pending ↔ completed
  - Switch between in_progress ↔ completed
  - Support unmarking completed tasks
  - Validate status transitions

- **Task Selection:**
  - List tasks with current status
  - Prompt for task ID
  - Validate task exists
  - Show current status clearly

- **Validation:**
  - Ensure task can be toggled
  - Check business rules for completion
  - Validate input task ID
  - Handle edge cases

- **Toggle Confirmation:**
  - Show status change clearly
  - Confirm successful toggle
  - Display updated task
  - Show completion statistics (e.g., "3 of 10 completed")

#### Error Scenarios:
- Task not found
- Invalid status transition
- Already in target state
- Toggle operation failed

---

## Common UI/UX Principles (All Subagents)

### User Experience:
- **Clear Prompts:** Use simple, actionable language
- **Visual Feedback:** Show progress, success, errors clearly
- **Error Messages:** Helpful, not cryptic
- **Confirmation:** For destructive actions
- **Cancellation:** Always allow users to abort
- **Consistency:** Similar workflows across operations

### Input Handling:
- **Validation First:** Check before processing
- **Graceful Errors:** Don't crash, guide users
- **Re-prompting:** Allow retry on invalid input
- **Defaults:** Provide sensible defaults where possible
- **Examples:** Show format examples when needed

### Output Formatting:
- **Readable Layout:** Use tables, lists, spacing
- **Color Coding:** Status indicators (if supported)
- **Alignment:** Proper column alignment
- **Truncation:** Handle long text gracefully
- **Summary Stats:** Show counts, totals, percentages

### Error Handling:
- **User-Friendly:** No stack traces to users
- **Actionable:** Tell users what to do next
- **Specific:** Explain what went wrong
- **Recovery:** Offer alternatives when possible
- **Logging:** Log errors for debugging (not shown to user)

---

## Integration Standards

### Domain Layer Interaction:
- **Call domain methods** for all business logic
- **Never bypass** domain validation
- **Handle domain exceptions** and translate to user messages
- **Respect business rules** enforced by domain
- **Use proper DTOs** for data transfer

### Application Layer Interaction:
- **Use application services** for workflows
- **Coordinate** multiple domain operations
- **Handle transactions** properly
- **Manage state** through application layer
- **Follow dependency flow**

### Validation Boundaries:
- **CLI validates:** User input format
- **Application validates:** Business workflow rules
- **Domain validates:** Core business logic
- **Don't duplicate:** Validation across layers

---

## Testing Requirements

### Unit Tests:
- Test input validation logic
- Test error message generation
- Test formatting functions
- Mock domain/application layers

### Integration Tests:
- Test complete workflows
- Test error paths
- Test user cancellation
- Test with actual domain layer

### User Acceptance Tests:
- Test with real user scenarios
- Verify readable output
- Check error message clarity
- Validate workflow intuitiveness

---

## Performance Considerations

- **Fast Response:** User operations < 100ms
- **Efficient Display:** Paginate large lists
- **Memory Usage:** Don't load unnecessary data
- **Batch Operations:** Support bulk actions when needed

---

## Future Extensibility

- **Plugin System:** Allow custom formatters
- **Themes:** Support different color schemes
- **Export:** Allow exporting task lists
- **Import:** Support importing tasks
- **Scripting:** Enable automation of common workflows

---

**Last Updated:** 2026-01-04
**Related Agents:** cli-add-task, task-deleter, task-updater, cli-task-viewer, cli-task-toggler
**Version:** 1.0
