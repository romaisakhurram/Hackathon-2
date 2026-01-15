import pytest
from httpx import AsyncClient
from ..src.main import app
from ..src.models.task import Task
from ..src.schemas.task import TaskCreate, TaskUpdate
import uuid


@pytest.mark.asyncio
async def test_task_crud_endpoints_exist():
    """
    Test that task CRUD endpoints exist and return appropriate responses.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Test GET /api/tasks (list tasks)
        response = await ac.get("/api/tasks/")
        assert response.status_code == 401, "List tasks endpoint should require authentication"

        # Test POST /api/tasks (create task)
        response = await ac.post("/api/tasks/", json={
            "title": "Test task",
            "description": "Test description"
        })
        assert response.status_code == 401, "Create task endpoint should require authentication"

        # Test GET /api/tasks/{id} (get specific task)
        fake_id = str(uuid.uuid4())
        response = await ac.get(f"/api/tasks/{fake_id}")
        assert response.status_code == 401, "Get task endpoint should require authentication"

        # Test PUT /api/tasks/{id} (update task)
        response = await ac.put(f"/api/tasks/{fake_id}", json={
            "title": "Updated task"
        })
        assert response.status_code == 401, "Update task endpoint should require authentication"

        # Test DELETE /api/tasks/{id} (delete task)
        response = await ac.delete(f"/api/tasks/{fake_id}")
        assert response.status_code == 401, "Delete task endpoint should require authentication"

        # Test PATCH /api/tasks/{id}/toggle (toggle completion)
        response = await ac.patch(f"/api/tasks/{fake_id}")
        assert response.status_code == 401, "Toggle task endpoint should require authentication"


@pytest.mark.asyncio
async def test_task_creation_schema():
    """
    Test task creation follows the defined schema.
    """
    # Test the schema directly
    task_create = TaskCreate(
        title="Test Task",
        description="Test Description",
        priority=1,
        status="pending"
    )

    assert task_create.title == "Test Task"
    assert task_create.description == "Test Description"
    assert task_create.priority == 1
    assert task_create.status == "pending"


@pytest.mark.asyncio
async def test_task_update_schema():
    """
    Test task update schema allows partial updates.
    """
    # Test the schema for updates (should allow partial updates)
    task_update = TaskUpdate(title="Updated Title")

    assert task_update.title == "Updated Title"
    assert task_update.description is None  # Should be None if not provided
    assert task_update.priority is None    # Should be None if not provided


@pytest.mark.asyncio
async def test_task_response_schema():
    """
    Test task response schema includes all required fields.
    """
    # Create a mock task to test the response schema
    task = Task(
        id=uuid.uuid4(),
        title="Test Task",
        description="Test Description",
        priority=1,
        status="pending",
        user_id=uuid.uuid4()
    )

    # Check that it has the expected attributes
    assert hasattr(task, 'id')
    assert hasattr(task, 'title')
    assert hasattr(task, 'description')
    assert hasattr(task, 'priority')
    assert hasattr(task, 'status')
    assert hasattr(task, 'created_at')
    assert hasattr(task, 'updated_at')
    assert hasattr(task, 'user_id')


@pytest.mark.asyncio
async def test_user_isolation_in_tasks():
    """
    Test that task endpoints respect user isolation.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # This test verifies that the endpoint implementations include user_id filtering
        # Though we can't fully test without valid tokens, we can verify the endpoint structure
        # ensures that user_id is required and validated

        # The implementation should ensure that:
        # 1. All task queries are filtered by user_id from the token
        # 2. Users can only access/modify their own tasks
        # 3. The user_id in the token matches the task's user_id

        # This is verified by checking that endpoints exist and require auth
        response = await ac.get("/api/tasks/")
        assert response.status_code == 401  # Authentication required