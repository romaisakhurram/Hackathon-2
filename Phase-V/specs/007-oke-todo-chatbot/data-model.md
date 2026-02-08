# Data Model: OKE Todo Chatbot System

## Entity: User
- **Fields**:
  - userId (string, unique, required)
  - username (string, unique, required)
  - email (string, unique, required)
  - hashedPassword (string, required)
  - createdAt (timestamp, required)
  - updatedAt (timestamp, required)
  - isActive (boolean, default: true)
  - roles (array of strings, default: ["user"])

- **Relationships**:
  - One-to-many with Task (user owns tasks)
  - One-to-many with ChatSession (user has multiple sessions)

- **Validation rules**:
  - Email must be valid format
  - Username must be 3-30 characters
  - Password must meet complexity requirements

## Entity: Task
- **Fields**:
  - taskId (string, unique, required)
  - title (string, required)
  - description (string, optional)
  - status (string, required, values: "pending", "in-progress", "completed")
  - priority (string, default: "medium", values: "low", "medium", "high")
  - dueDate (timestamp, optional)
  - ownerId (string, required, references User.userId)
  - createdAt (timestamp, required)
  - updatedAt (timestamp, required)
  - completedAt (timestamp, optional)

- **Relationships**:
  - Many-to-one with User (task belongs to user)
  - One-to-many with Notification (task can trigger notifications)

- **Validation rules**:
  - Title must be 1-100 characters
  - Status must be one of allowed values
  - Due date must be in the future if provided

## Entity: ChatSession
- **Fields**:
  - sessionId (string, unique, required)
  - userId (string, required, references User.userId)
  - startedAt (timestamp, required)
  - endedAt (timestamp, optional)
  - isActive (boolean, default: true)
  - metadata (JSON object, optional)

- **Relationships**:
  - Many-to-one with User (session belongs to user)
  - One-to-many with Message (session contains messages)

- **Validation rules**:
  - Session must belong to a valid user
  - Cannot have multiple active sessions per user

## Entity: Message
- **Fields**:
  - messageId (string, unique, required)
  - sessionId (string, required, references ChatSession.sessionId)
  - senderType (string, required, values: "user", "bot")
  - content (string, required)
  - timestamp (timestamp, required)
  - messageType (string, default: "text", values: "text", "command", "notification")

- **Relationships**:
  - Many-to-one with ChatSession (message belongs to session)

- **Validation rules**:
  - Content must be 1-1000 characters
  - Sender type must be one of allowed values

## Entity: Notification
- **Fields**:
  - notificationId (string, unique, required)
  - taskId (string, required, references Task.taskId)
  - userId (string, required, references User.userId)
  - type (string, required, values: "reminder", "due-date", "completion")
  - message (string, required)
  - scheduledTime (timestamp, required)
  - sentAt (timestamp, optional)
  - status (string, default: "pending", values: "pending", "sent", "failed")

- **Relationships**:
  - Many-to-one with Task (notification related to task)
  - Many-to-one with User (notification sent to user)

- **Validation rules**:
  - Scheduled time must be in the future
  - Status must be one of allowed values