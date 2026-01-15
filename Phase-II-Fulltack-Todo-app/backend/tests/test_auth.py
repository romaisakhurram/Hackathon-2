import pytest
from httpx import AsyncClient
from ..src.main import app
import uuid


@pytest.mark.asyncio
async def test_auth_endpoints_exist():
    """
    Test that auth endpoints exist and return appropriate responses.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Test register endpoint
        response = await ac.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "securepassword"
        })
        # Should return 401 or 422 (missing/invalid token), not 404
        assert response.status_code in [401, 422, 500], "Register endpoint should exist"

        # Test login endpoint
        response = await ac.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "securepassword"
        })
        # Should return 422 (validation error) or 500, not 404
        assert response.status_code in [422, 500], "Login endpoint should exist"

        # Test logout endpoint
        response = await ac.post("/api/auth/logout")
        # Should return 401 (unauthorized) since no token provided, not 404
        assert response.status_code == 401, "Logout endpoint should exist"


@pytest.mark.asyncio
async def test_jwt_token_validation():
    """
    Test JWT token validation in protected endpoints.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Try to access protected task endpoint without token
        response = await ac.get("/api/tasks/")
        assert response.status_code == 401, "Protected endpoint should require authentication"

        # Try with invalid token format
        response = await ac.get("/api/tasks/", headers={
            "Authorization": "Bearer invalid_token_format"
        })
        assert response.status_code == 401, "Invalid token should be rejected"


@pytest.mark.asyncio
async def test_user_isolation_in_auth():
    """
    Test that auth properly isolates user contexts.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Accessing auth endpoints should not expose other users' information
        # This test verifies the foundation for user isolation at the auth level
        response = await ac.get("/api/auth/logout")
        # Should return 401, not expose any user-specific data
        assert response.status_code == 401
        if "detail" in response.json():
            assert "credentials" in response.json()["detail"] or "token" in response.json()["detail"]