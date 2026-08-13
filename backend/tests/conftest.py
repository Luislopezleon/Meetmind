import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from unittest.mock import AsyncMock, patch

from app.main import app
from app.db.database import get_db, Base
from app.db.redis import redis_manager
from app.core.config import settings


# Test database URL (SQLite in-memory for speed)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def mock_redis():
    """Mock Redis for testing."""
    # Mock the redis manager
    original_redis = redis_manager.redis_client
    redis_manager.redis_client = AsyncMock()
    
    # Setup mock behaviors
    redis_manager.redis_client.ping.return_value = True
    redis_manager.redis_client.setex.return_value = True
    redis_manager.redis_client.get.return_value = None
    redis_manager.redis_client.delete.return_value = True
    redis_manager.redis_client.publish.return_value = 1
    
    yield redis_manager.redis_client
    
    # Restore original
    redis_manager.redis_client = original_redis


@pytest.fixture(autouse=True)
def mock_recall_service():
    """Mock Recall.ai service for all tests to avoid real API calls."""
    call_counter = {"count": 0}
    
    async def mock_create_bot(*args, **kwargs):
        call_counter["count"] += 1
        return {
            "id": f"test-bot-{call_counter['count']}",
            "meeting_url": "https://meet.google.com/test",
            "status_changes": []
        }
    
    with patch('app.api.routes.meetings.recall_service') as mock_service:
        mock_service.create_bot = AsyncMock(side_effect=mock_create_bot)
        mock_service.get_bot_status = AsyncMock(return_value={
            "id": "test-bot-123",
            "status_changes": [{"code": "ready"}],
            "meeting_participants": []
        })
        mock_service.get_bot_transcript = AsyncMock(return_value=[])
        mock_service.delete_bot = AsyncMock(return_value=True)
        mock_service.get_current_status = lambda x: x[-1]["code"] if x else "unknown"
        yield mock_service


@pytest.fixture
def sample_meeting_data():
    """Sample meeting data for tests."""
    return {
        "title": "Test Meeting",
        "meeting_url": "https://meet.google.com/test-meeting",
        "platform": "google_meet",
        "scheduled_at": "2026-08-15T10:00:00Z",
        "participants": ["Luis", "María"]
    }


@pytest.fixture
def sample_transcript_data():
    """Sample transcript data for tests."""
    return {
        "text": "Hola, vamos a empezar la reunión",
        "speaker_name": "Luis",
        "speaker_id": "speaker_1",
        "confidence": 0.95,
        "start_time": 0.0,
        "end_time": 3.2
    }


@pytest.fixture
def sample_action_item_data():
    """Sample action item data for tests."""
    return {
        "task": "Enviar informe de ventas",
        "assignee": "Luis",
        "deadline": "viernes",
        "priority": "high",
        "confidence_score": 0.87
    }


# Test configurations
@pytest.fixture(autouse=True)
def setup_test_settings():
    """Override settings for testing."""
    original_env = settings.environment
    settings.environment = "test"
    
    yield
    
    # Restore
    settings.environment = original_env