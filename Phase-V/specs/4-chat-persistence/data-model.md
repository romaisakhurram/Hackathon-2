# Data Model: Chat API & Persistence

## Entities

### Conversation
- **id** (integer): Unique identifier for the conversation
- **user_id** (string): Reference to the user who owns this conversation
- **created_at** (timestamp): Timestamp when the conversation was created
- **updated_at** (timestamp): Timestamp when the conversation was last updated
- **title** (string, nullable): Optional title for the conversation (generated from first message if not provided)

### Message
- **id** (integer): Unique identifier for the message
- **conversation_id** (integer): Reference to the conversation this message belongs to
- **user_id** (string): Reference to the user who sent this message (the sender)
- **role** (string): Role of the message sender ('user' for human, 'assistant' for AI agent)
- **content** (string): The actual message content (up to 2000 characters)
- **created_at** (timestamp): Timestamp when the message was created
- **metadata** (json, nullable): Additional metadata for the message (e.g., tool calls, response details)

## Relationships
- Conversation 1-* Message (one conversation contains many messages)
- User 1-* Conversation (one user has many conversations)
- User 1-* Message (one user sends many messages)

## Validation Rules
- All messages must have a valid conversation_id
- All messages must have a valid user_id (sender)
- Role must be either 'user' or 'assistant'
- Content length must not exceed 2000 characters
- User can only access conversations and messages they own
- Conversation user_id must match the authenticated user for access

## State Transitions
- Conversation: CREATED → ACTIVE → INACTIVE (when conversation is no longer actively used)
- Message: PENDING → SAVED (once successfully stored in database)

## Indexes
- Conversation: index on user_id for efficient user conversation retrieval
- Message: composite index on (conversation_id, created_at) for chronological message loading
- Message: index on user_id for efficient user message queries