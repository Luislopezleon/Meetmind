import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.schemas import HealthCheck


class TestHealthEndpoint:
    """Test health check endpoint functionality."""
    
    def test_health_check_success(self, client: TestClient, mock_redis):
        """Test health check when all services are healthy."""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
        
        # Verify overall status
        assert data["status"] == "healthy"
        
        # Verify service statuses
        services = data["services"]
        assert "api" in services
        assert "database" in services  
        assert "redis" in services
        
        assert services["api"] == "healthy"
        assert services["database"] == "healthy"
        assert services["redis"] == "healthy"
    
    def test_health_check_database_unhealthy(self, client: TestClient, mock_redis):
        """Test health check when database is down."""
        # Mock database error by patching the db session
        with patch('app.api.routes.health.get_db') as mock_get_db:
            from unittest.mock import MagicMock
            mock_session = MagicMock()
            mock_session.execute.side_effect = Exception("Connection refused")
            
            def override_get_db():
                yield mock_session
            
            from app.main import app as fastapi_app
            from app.db.database import get_db
            fastapi_app.dependency_overrides[get_db] = override_get_db
            
            response = client.get("/health/")
            
            fastapi_app.dependency_overrides.pop(get_db, None)
            
            assert response.status_code == 200
            data = response.json()
            
            # Overall status should be unhealthy
            assert data["status"] == "unhealthy"
            
            # Database should be marked as unhealthy
            services = data["services"]
            assert "unhealthy" in services["database"]
    
    def test_health_check_redis_unhealthy(self, client: TestClient):
        """Test health check when Redis is down."""
        with patch('app.api.routes.health.redis_manager') as mock_rm:
            # Mock Redis connection error
            mock_rm.redis_client = AsyncMock()
            mock_rm.redis_client.ping = AsyncMock(side_effect=Exception("Redis connection failed"))
            
            response = client.get("/health/")
            
            assert response.status_code == 200
            data = response.json()
            
            # Overall status should be unhealthy
            assert data["status"] == "unhealthy"
            
            # Redis should be marked as unhealthy
            services = data["services"]
            assert "unhealthy" in services["redis"]
    
    def test_health_check_redis_not_connected(self, client: TestClient):
        """Test health check when Redis manager is not initialized."""
        with patch('app.api.routes.health.redis_manager') as mock_rm:
            # Mock Redis not connected
            mock_rm.redis_client = None
            
            response = client.get("/health/")
            
            assert response.status_code == 200
            data = response.json()
            
            # Overall status should be unhealthy  
            assert data["status"] == "unhealthy"
            
            # Redis should be marked as unhealthy
            services = data["services"]
            assert services["redis"] == "unhealthy: not connected"
    
    def test_health_check_response_schema(self, client: TestClient, mock_redis):
        """Test that health check response matches expected schema."""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the response can be parsed as HealthCheck schema
        health_check = HealthCheck(**data)
        
        assert health_check.status in ["healthy", "unhealthy"]
        assert health_check.timestamp is not None
        assert health_check.version == "1.0.0"
        assert isinstance(health_check.services, dict)
    
    def test_health_check_timing(self, client: TestClient, mock_redis):
        """Test that health check responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/health/")
        end_time = time.time()
        
        # Health check should respond in under 1 second
        assert (end_time - start_time) < 1.0
        assert response.status_code == 200
    
    def test_health_check_multiple_calls(self, client: TestClient, mock_redis):
        """Test multiple consecutive health check calls."""
        # Make multiple calls to ensure consistency
        responses = []
        for _ in range(3):
            response = client.get("/health/")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"