# Deployment Guide: Todo AI Chatbot with Chat Persistence

## Overview
This guide provides instructions for deploying the Todo AI Chatbot with chat persistence functionality to production environments.

## Prerequisites

### System Requirements
- Python 3.11 or higher
- Node.js 18+ (for frontend, if deployed separately)
- PostgreSQL-compatible database (Neon recommended)
- Redis (for rate limiting, if using Redis-based rate limiter)
- At least 1GB available RAM
- At least 5GB available disk space

### Environment Setup
Before deployment, ensure the following environment variables are configured:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET="your-secure-jwt-secret-key-here"

# Database Configuration
DATABASE_URL="postgresql://username:password@host:port/database_name"
NEON_DATABASE_URL="your-neon-postgres-connection-string"

# AI Provider Configuration (OpenRouter)
OPENAI_API_KEY="your-openrouter-api-key"
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_MODEL="gpt-4"  # or other supported model

# Rate Limiting (Optional)
RATE_LIMIT_REQUESTS_PER_MINUTE=10

# Application Settings
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
BACKEND_CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"  # Comma-separated list
```

## Deployment Steps

### 1. Clone and Setup Repository
```bash
git clone https://github.com/your-org/todo-ai-chatbot.git
cd todo-ai-chatbot

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 2. Database Setup
```bash
# Run database migrations (or initialize the database)
cd backend
python -m src.init_db

# Verify database connection
python -c "from src.database import check_database_connection; import asyncio; print(asyncio.run(check_database_connection()))"
```

### 3. Configuration Validation
```bash
# Run startup validation checks
python -c "from src.utils.config_validator import run_startup_validation; run_startup_validation()"
```

### 4. Start the Backend Service
```bash
# Using uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn (if installed)
gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. Verify Deployment
```bash
# Test the health endpoint
curl http://localhost:8000/health

# Test the chat endpoint (with proper authentication)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/user-id/chat \
     -d '{"message": "Hello, test message"}'
```

## Scaling Recommendations

### Horizontal Scaling
- Use a load balancer to distribute traffic across multiple backend instances
- Ensure shared database connection pool settings are optimized
- Use Redis for session management and rate limiting if scaling beyond a single instance
- Configure sticky sessions if maintaining any server-side session state (though the chat API is stateless)

### Database Optimization
- Use connection pooling (SQLAlchemy's built-in pool is used by default)
- Set appropriate pool sizes based on expected concurrent connections
- Monitor slow query logs and optimize frequently used queries
- Consider read replicas for heavy read operations

### Performance Tuning
- Adjust the number of workers based on CPU cores (typically 2 * CPU cores + 1)
- Configure appropriate timeout values for AI provider calls
- Set up monitoring for response times and error rates

## Security Considerations

### Authentication & Authorization
- Ensure JWT secrets are stored securely (not in code)
- Regularly rotate JWT secrets
- Validate that users can only access their own conversations
- Implement proper rate limiting to prevent abuse

### Data Protection
- Encrypt sensitive data in transit using HTTPS
- Consider encrypting sensitive data at rest
- Regularly backup database content
- Implement proper audit logging for sensitive operations

### API Security
- Validate all inputs to prevent injection attacks
- Implement proper rate limiting per user
- Sanitize outputs to prevent XSS in frontend applications
- Monitor for unusual access patterns

## Monitoring and Logging

### Key Metrics to Monitor
- API response times
- Error rates
- Active conversations
- Database connection pool usage
- AI provider response times
- Rate limit hits

### Log Configuration
- Set LOG_LEVEL to INFO for production (WARNING for high-volume deployments)
- Ensure logs are properly rotated to prevent disk space issues
- Consider structured logging for easier analysis
- Log security-relevant events (failed auth attempts, etc.)

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Verify DATABASE_URL is correctly set
- Check firewall rules allow connections to database
- Confirm database credentials are valid

#### AI Provider Issues
- Verify OPENAI_API_KEY is correctly set
- Check if OpenRouter API is accessible from your deployment environment
- Confirm the specified model is available

#### Authentication Problems
- Ensure BETTER_AUTH_SECRET matches between frontend and backend
- Verify JWT tokens are being passed correctly in Authorization header
- Check that token expiration is handled properly

#### Rate Limiting Issues
- Verify rate limiting configuration
- Check if legitimate users are being blocked incorrectly
- Adjust rate limits if needed based on usage patterns

### Debugging Commands
```bash
# Check application health
curl http://your-domain.com/health

# Verify configuration
python -c "from src.utils.config_validator import get_config_validation_report; print(get_config_validation_report())"

# Check database connection
python -c "from src.database import get_async_session; import asyncio; async def test(): async with get_async_session() as s: print('DB connected'); asyncio.run(test())"
```

## Maintenance Tasks

### Regular Maintenance
- Monitor and rotate JWT secrets periodically
- Review and archive old conversations to manage database size
- Update dependencies regularly
- Monitor API usage for rate limiting adjustments

### Backup Strategy
- Schedule regular database backups
- Test backup restoration procedures periodically
- Store backups securely with restricted access

## Rollback Procedure

If issues occur after deployment:

1. Stop the new application instances
2. Restore the previous version
3. Verify database schema compatibility
4. Restart with the previous version
5. Monitor for stability

## Environment-Specific Configurations

### Development
```bash
LOG_LEVEL="DEBUG"
DATABASE_URL="postgresql://localhost:5432/todo_dev"
OPENAI_MODEL="gpt-3.5-turbo"  # Potentially cheaper model for dev
```

### Staging
```bash
LOG_LEVEL="INFO"
DATABASE_URL="postgresql://staging-db-url"
OPENAI_MODEL="gpt-4"  # Same as production
```

### Production
```bash
LOG_LEVEL="WARNING"
DATABASE_URL="postgresql://production-db-url"
OPENAI_MODEL="gpt-4"  # Production model
RATE_LIMIT_REQUESTS_PER_MINUTE=10
BACKEND_CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

## Health Checks

Configure your deployment platform to perform health checks at:
- `/health` endpoint for application health
- Verify response includes `"status": "healthy"` and `"db": "healthy"`

## Next Steps

After successful deployment:
1. Perform smoke tests with the chat API
2. Verify user isolation is working properly
3. Test conversation persistence across restarts
4. Monitor performance metrics and adjust as needed