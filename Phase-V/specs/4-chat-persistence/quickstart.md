# Quickstart: Chat API & Persistence

## Prerequisites

1. **Ensure Phase III AI agent and MCP integration is running**:
   - AI agent service must be accessible
   - MCP tools must be available and functional
   - JWT authentication must be properly configured

## Setup

1. **Environment Variables**:
   ```bash
   # Database configuration (existing Neon PostgreSQL)
   export DATABASE_URL="your-neon-postgres-url"

   # JWT configuration (existing Better Auth)
   export BETTER_AUTH_SECRET="your-jwt-secret"

   # AI provider configuration (OpenRouter)
   export OPENAI_API_KEY="your-openrouter-api-key"
   export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
   export OPENAI_MODEL="gpt-4"  # or other supported model
   ```

2. **Install Dependencies**:
   ```bash
   # In the backend directory
   pip install fastapi sqlmodel pydantic python-jose[cryptography] passlib[bcrypt] python-multipart
   ```

## Running the Chat API

1. **Start the Backend Service**:
   ```bash
   # In the backend directory
   uvicorn src.main:app --reload --port 8000
   ```

2. **Test the Chat Endpoint**:
   ```bash
   # Example request with JWT token
   curl -X POST "http://localhost:8000/api/user-id-123/chat" \
     -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, how can I add a task?", "conversation_id": 123}'
   ```

## Using the Chat API

1. **Start a new conversation**:
   - Send POST request without conversation_id to create a new conversation
   - The API will return a new conversation_id

2. **Continue an existing conversation**:
   - Send POST request with conversation_id to continue an existing conversation
   - The API will load the conversation context from the database

3. **Monitor rate limits**:
   - The system enforces 10 requests per minute per user
   - Excessive requests will return 429 status code

## Development

1. **Run tests**:
   ```bash
   # Unit tests
   pytest tests/unit/models/
   pytest tests/unit/services/
   pytest tests/unit/api/

   # Integration tests
   pytest tests/integration/chat_integration_test.py

   # Contract tests
   pytest tests/contract/chat_api_contract_test.py
   ```

2. **Database migrations**:
   ```bash
   # Create new conversation and message tables
   # Tables will be created automatically on first run
   ```

## Troubleshooting

- **Authentication errors**: Verify JWT tokens and Better Auth configuration
- **Database connection issues**: Check DATABASE_URL and connection pool settings
- **Rate limiting**: Monitor request frequency per user_id
- **Conversation continuity**: Verify conversation_id is properly passed between requests
- **Message persistence**: Check that both user and AI messages are saved to the database