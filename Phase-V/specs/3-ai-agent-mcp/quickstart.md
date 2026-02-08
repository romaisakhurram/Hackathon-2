# Quickstart: AI Agent + MCP Integration

## Prerequisites

1. **Ensure Phase II backend is running**:
   - Backend API must be accessible at the configured endpoint
   - Better Auth authentication must be functional
   - Task CRUD endpoints must be available

## Setup

1. **Environment Variables**:
   ```bash
   # OpenRouter configuration
   export OPENAI_API_KEY="your-openrouter-api-key"
   export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
   export OPENAI_MODEL="gpt-4"  # or other supported model

   # Backend API configuration (existing Phase II)
   export BACKEND_API_URL="http://localhost:8000"  # Adjust to your backend URL
   export BETTER_AUTH_SECRET="your-jwt-secret"  # Same as Phase II
   ```

2. **Install Dependencies**:
   ```bash
   cd ai-agent-mcp
   pip install openai mcp-sdk python-dotenv requests
   ```

## Running the AI Agent

1. **Start the MCP Server**:
   ```bash
   cd ai-agent-mcp
   python -m src.mcp_server.server
   ```

2. **Test the AI Agent**:
   ```bash
   cd ai-agent-mcp
   # For development/testing
   python -m src.ai_agent.agent --test-mode
   ```

## Using the Chat Interface

1. **Access the endpoint** that connects the AI agent to the MCP tools
2. **Send natural language requests** like:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Complete task #1"
   - "Update task #2 to have high priority"

## Development

1. **Run tests**:
   ```bash
   cd ai-agent-mcp
   pytest tests/unit/ai_agent/
   pytest tests/unit/mcp_server/
   pytest tests/integration/chat_integration_test.py
   ```

2. **Validate MCP tools**:
   ```bash
   cd ai-agent-mcp
   pytest tests/contract/mcp_tool_contracts_test.py
   ```

## Troubleshooting

- **Authentication errors**: Verify JWT tokens match Phase II Better Auth configuration
- **Backend connectivity**: Ensure BACKEND_API_URL points to running Phase II backend
- **Tool timeouts**: Check 30-second timeout configuration in MCP tools
- **Intent recognition**: Review confidence thresholds (80% default)
- **User isolation**: Confirm ownership validation is working with existing backend