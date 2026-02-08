"""
Health check endpoints for the Todo AI Chatbot.
Provides health and readiness probes for Kubernetes.
"""
from fastapi import APIRouter
from datetime import datetime
import logging

# Create router
router = APIRouter(prefix="/health", tags=["health"])

# Get logger
logger = logging.getLogger(__name__)

@router.get("/live", status_code=200)
async def liveness_check():
    """
    Liveness probe endpoint.
    Returns 200 if the service is running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "todo-chatbot-backend"
    }

@router.get("/ready", status_code=200)
async def readiness_check():
    """
    Readiness probe endpoint.
    Returns 200 if the service is ready to accept requests.
    In a real implementation, this would check database connectivity,
    external service availability, etc.
    """
    # In a real implementation, you would check:
    # - Database connectivity
    # - External service availability
    # - Resource availability
    # For now, we'll just return that we're ready
    
    try:
        # Simulate checking critical dependencies
        # This is where you would check database, Redis, etc.
        checks = {
            "database": "connected",  # Would check actual DB connection
            "redis": "connected",     # Would check actual Redis connection
            "external_apis": "available"  # Would check external API availability
        }
        
        # If all checks pass, return ready
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "todo-chatbot-backend",
            "checks": checks
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "todo-chatbot-backend",
            "error": str(e)
        }, 503

@router.get("/", status_code=200)
async def health_check():
    """
    General health check endpoint.
    Returns the overall health of the service.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "todo-chatbot-backend",
        "version": "1.0.0"
    }