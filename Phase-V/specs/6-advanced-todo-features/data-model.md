# Data Model: Advanced Todo Features

## Overview
This document defines the data models for the advanced todo features including recurring tasks, due dates, reminders, priorities, tags, and related entities.

## Entity: Task
The primary entity representing a user's activity.

**Fields:**
- `id` (UUID, Primary Key): Unique identifier for the task
- `title` (VARCHAR(255), NOT NULL): Title of the task
- `description` (TEXT): Detailed description of the task
- `status` (ENUM: 'pending', 'in-progress', 'completed', 'cancelled'): Current status of the task
- `userId` (UUID, Foreign Key): Reference to the user who owns the task
- `createdAt` (TIMESTAMP): When the task was created
- `updatedAt` (TIMESTAMP): When the task was last updated
- `dueDate` (TIMESTAMP, NULLABLE): When the task is due
- `completedAt` (TIMESTAMP, NULLABLE): When the task was completed
- `priorityId` (UUID, Foreign Key, NULLABLE): Reference to the priority level
- `parentId` (UUID, Foreign Key, NULLABLE): Reference to parent task for recurring tasks
- `recurrenceRuleId` (UUID, Foreign Key, NULLABLE): Reference to recurrence rules for recurring tasks
- `isTemplate` (BOOLEAN, DEFAULT FALSE): Whether this is a template for recurring tasks

**Relationships:**
- One-to-many with Reminder (one task can have multiple reminders)
- Many-to-many with Tag (through task_tags junction table)
- One-to-one with RecurrenceRule (optional)
- One-to-many with child tasks (for recurring tasks)

**Validation Rules:**
- Title must be 1-255 characters
- Status must be one of the allowed values
- Due date must be in the future if provided
- ParentId and recurrenceRuleId must both be set or both null for recurring tasks

## Entity: RecurrenceRule
Defines the pattern for recurring tasks.

**Fields:**
- `id` (UUID, Primary Key): Unique identifier for the rule
- `interval` (ENUM: 'daily', 'weekly', 'monthly', 'yearly', 'custom'): How often the task recurs
- `frequency` (INTEGER, DEFAULT 1): How many intervals between recurrences (e.g., every 2 weeks)
- `daysOfWeek` (SMALLINT[], NULLABLE): Days of week for weekly recurrences (0=Sunday, 1=Monday, etc.)
- `dayOfMonth` (INTEGER, NULLABLE): Day of month for monthly recurrences
- `endDate` (TIMESTAMP, NULLABLE): When the recurrence should stop
- `occurrenceCount` (INTEGER, NULLABLE): Max number of occurrences (alternative to endDate)
- `createdAt` (TIMESTAMP): When the rule was created
- `updatedAt` (TIMESTAMP): When the rule was last updated

**Relationships:**
- Many-to-one with Task (many tasks can share the same rule, though typically one-to-one)

**Validation Rules:**
- Interval must be one of the allowed values
- Frequency must be >= 1
- DaysOfWeek values must be 0-6 when interval is weekly
- DayOfMonth must be 1-31 when interval is monthly
- Either endDate or occurrenceCount must be set (not both null)

## Entity: Reminder
Notification settings for tasks.

**Fields:**
- `id` (UUID, Primary Key): Unique identifier for the reminder
- `taskId` (UUID, Foreign Key): Reference to the task this reminder is for
- `scheduledTime` (TIMESTAMP): When the reminder should be triggered
- `method` (ENUM: 'email', 'push', 'sms', 'in-app'): How the reminder should be delivered
- `sent` (BOOLEAN, DEFAULT FALSE): Whether the reminder has been sent
- `sentAt` (TIMESTAMP, NULLABLE): When the reminder was actually sent
- `createdAt` (TIMESTAMP): When the reminder was created
- `updatedAt` (TIMESTAMP): When the reminder was last updated

**Relationships:**
- Many-to-one with Task (one task can have multiple reminders)

**Validation Rules:**
- Scheduled time must be before the task's due date
- Method must be one of the allowed values

## Entity: Tag
User-defined labels for categorizing tasks.

**Fields:**
- `id` (UUID, Primary Key): Unique identifier for the tag
- `name` (VARCHAR(50), NOT NULL): Name of the tag
- `color` (VARCHAR(7), DEFAULT '#000000'): Color associated with the tag (hex format)
- `userId` (UUID, Foreign Key): Reference to the user who owns the tag
- `createdAt` (TIMESTAMP): When the tag was created
- `updatedAt` (TIMESTAMP): When the tag was last updated
- `deletedAt` (TIMESTAMP, NULLABLE): When the tag was soft-deleted

**Relationships:**
- Many-to-many with Task (through task_tags junction table)

**Validation Rules:**
- Name must be 1-50 characters
- Color must be in valid hex format (#XXXXXX)
- Name must be unique per user

## Entity: Priority
Enumerated values for task importance.

**Fields:**
- `id` (UUID, Primary Key): Unique identifier for the priority
- `name` (VARCHAR(20), NOT NULL): Display name of the priority ('High', 'Medium', 'Low')
- `value` (INTEGER, NOT NULL): Numeric value for ordering (1=High, 2=Medium, 3=Low)
- `color` (VARCHAR(7), NOT NULL): Color associated with the priority (hex format)

**Relationships:**
- One-to-many with Task (one priority can be assigned to many tasks)

**Validation Rules:**
- Name must be one of 'High', 'Medium', 'Low'
- Value must be 1, 2, or 3
- Color must be in valid hex format

## Junction Table: task_tags
Connects tasks and tags in a many-to-many relationship.

**Fields:**
- `taskId` (UUID, Foreign Key): Reference to the task
- `tagId` (UUID, Foreign Key): Reference to the tag
- `createdAt` (TIMESTAMP): When the association was created

**Constraints:**
- Composite primary key (taskId, tagId)
- Prevent duplicate associations

## Indexes
- Task: userId (for user-specific queries), dueDate (for due date filtering), status (for status filtering)
- Reminder: taskId (for task-specific queries), scheduledTime (for scheduler queries), sent (for scheduler queries)
- Tag: userId and name (for user-specific tag queries), deletedAt (for soft-delete queries)
- task_tags: taskId and tagId (for efficient joins)