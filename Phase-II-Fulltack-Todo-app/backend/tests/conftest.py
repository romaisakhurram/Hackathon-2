import pytest
import asyncio
from httpx import AsyncClient
from ..src.main import app
from ..src.database import async_engine, get_async_session
from ..src.models.task import Task
from ..src.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from typing import AsyncGenerator
import uuid
from datetime import datetime


# Use an in-memory database for testing or a separate test database
TEST_DATABASE_URL = "postgresql://neondb_owner:npg_iI4QRn6lawJe@ep-raspy-cake-absxlcnr-pooler.eu-west-2.aws.neon.tech/test_neondb?sslmode=require&channel_binding=require"


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    """
    Create an async client for testing.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def db_session():
    """
    Create a database session for testing.
    """
    async with AsyncSession(async_engine) as session:
        yield session


@pytest.fixture
async def sample_user(db_session):
    """
    Create a sample user for testing.
    """
    user = User(
        email="test@example.com",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_task(db_session, sample_user):
    """
    Create a sample task for testing.
    """
    task = Task(
        title="Test Task",
        description="This is a test task",
        priority=1,
        status="pending",
        user_id=sample_user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task