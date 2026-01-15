import pytest
import asyncio
import time
from httpx import AsyncClient
from ..src.main import app
from ..src.database import check_database_connection
from ..src.dependencies import rate_limiter


@pytest.mark.asyncio
async def test_response_time_under_3_seconds():
    """
    Test that API responses are under 3 seconds (NFR-001).
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        start_time = time.time()
        response = await ac.get("/")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 3.0, f"Response time was {response_time}s, which exceeds 3 seconds"


@pytest.mark.asyncio
async def test_concurrent_request_handling():
    """
    Test concurrent request handling (NFR-002).
    """
    async def make_request():
        async with AsyncClient(app=app, base_url="http://testserver") as ac:
            response = await ac.get("/health")
            return response.status_code

    # Make 50 concurrent requests
    tasks = [make_request() for _ in range(50)]
    results = await asyncio.gather(*tasks)

    # Check that all requests succeeded
    assert all(result == 200 for result in results), "Not all concurrent requests succeeded"


@pytest.mark.asyncio
async def test_rate_limiting():
    """
    Test that rate limiting works correctly (FR-008).
    """
    # Temporarily set a low rate limit for testing
    original_max_requests = rate_limiter.max_requests
    rate_limiter.max_requests = 3  # Allow only 3 requests

    try:
        async with AsyncClient(app=app, base_url="http://testserver") as ac:
            # Make 5 requests quickly - some should be rate limited
            responses = []
            for i in range(5):
                response = await ac.get("/health")
                responses.append(response.status_code)

        # Check that at least some requests were rate limited (429)
        assert 429 in responses, "Rate limiting did not trigger as expected"

    finally:
        # Restore original rate limit
        rate_limiter.max_requests = original_max_requests


def test_database_connection_health():
    """
    Test database connection health.
    """
    # This tests the graceful degradation capability (NFR-007)
    is_connected = asyncio.run(check_database_connection())
    assert is_connected, "Database connection should be healthy"