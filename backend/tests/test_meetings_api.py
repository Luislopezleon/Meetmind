import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock

from app.models import Meeting


class TestMeetingsAPI:
    """Test meetings API endpoints."""
    
    def test_create_meeting_success(self, client: TestClient, sample_meeting_data):
        """Test successful meeting creation."""
        response = client.post("/api/v1/meetings/", json=sample_meeting_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["title"] == sample_meeting_data["title"]
        assert data["meeting_url"] == sample_meeting_data["meeting_url"]
        assert data["platform"] == sample_meeting_data["platform"]
        assert data["status"] == "bot_created"
        assert data["participants"] == sample_meeting_data["participants"]
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_meeting_invalid_data(self, client: TestClient):
        """Test meeting creation with invalid data."""
        invalid_data = {
            "title": "",  # Empty title should fail
            "meeting_url": "not-a-valid-url",
            "platform": "invalid_platform",
            "scheduled_at": "invalid-date"
        }
        
        response = client.post("/api/v1/meetings/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_meeting_missing_required_fields(self, client: TestClient):
        """Test meeting creation with missing required fields."""
        incomplete_data = {
            "title": "Test Meeting"
            # Missing required fields
        }
        
        response = client.post("/api/v1/meetings/", json=incomplete_data)
        assert response.status_code == 422
    
    def test_get_meeting_success(self, client: TestClient, sample_meeting_data):
        """Test retrieving a specific meeting."""
        # First create a meeting
        create_response = client.post("/api/v1/meetings/", json=sample_meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/meetings/{meeting_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == meeting_id
        assert data["title"] == sample_meeting_data["title"]
    
    def test_get_meeting_not_found(self, client: TestClient):
        """Test retrieving a non-existent meeting."""
        response = client.get("/api/v1/meetings/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_list_meetings_empty(self, client: TestClient):
        """Test listing meetings when none exist."""
        response = client.get("/api/v1/meetings/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_meetings_with_data(self, client: TestClient, sample_meeting_data):
        """Test listing meetings when some exist."""
        # Create multiple meetings
        meeting_data_1 = sample_meeting_data.copy()
        meeting_data_1["title"] = "Meeting 1"
        
        meeting_data_2 = sample_meeting_data.copy()
        meeting_data_2["title"] = "Meeting 2"
        meeting_data_2["meeting_url"] = "https://meet.google.com/test-meeting-2"
        
        client.post("/api/v1/meetings/", json=meeting_data_1)
        client.post("/api/v1/meetings/", json=meeting_data_2)
        
        # List all meetings
        response = client.get("/api/v1/meetings/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        titles = [meeting["title"] for meeting in data]
        assert "Meeting 1" in titles
        assert "Meeting 2" in titles
    
    def test_list_meetings_pagination(self, client: TestClient, sample_meeting_data):
        """Test meetings list pagination."""
        # Create multiple meetings
        for i in range(5):
            meeting_data = sample_meeting_data.copy()
            meeting_data["title"] = f"Meeting {i}"
            meeting_data["meeting_url"] = f"https://meet.google.com/test-{i}"
            client.post("/api/v1/meetings/", json=meeting_data)
        
        # Test pagination
        response = client.get("/api/v1/meetings/?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_update_meeting_success(self, client: TestClient, sample_meeting_data):
        """Test successful meeting update."""
        # Create meeting
        create_response = client.post("/api/v1/meetings/", json=sample_meeting_data)
        meeting_id = create_response.json()["id"]
        
        # Update meeting
        update_data = {
            "title": "Updated Meeting Title",
            "status": "in_progress",
            "participants": ["Luis", "María", "Carlos"]
        }
        
        response = client.put(f"/api/v1/meetings/{meeting_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Meeting Title"
        assert data["status"] == "in_progress"
        assert len(data["participants"]) == 3
        assert "Carlos" in data["participants"]
    
    def test_update_meeting_partial(self, client: TestClient, sample_meeting_data):
        """Test partial meeting update (only some fields)."""
        # Create meeting
        create_response = client.post("/api/v1/meetings/", json=sample_meeting_data)
        meeting_id = create_response.json()["id"]
        original_title = create_response.json()["title"]
        
        # Partial update (only status)
        update_data = {"status": "completed"}
        
        response = client.put(f"/api/v1/meetings/{meeting_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["title"] == original_title  # Should remain unchanged
    
    def test_update_meeting_not_found(self, client: TestClient):
        """Test updating a non-existent meeting."""
        update_data = {"title": "New Title"}
        
        response = client.put("/api/v1/meetings/99999", json=update_data)
        
        assert response.status_code == 404
    
    def test_delete_meeting_success(self, client: TestClient, sample_meeting_data):
        """Test successful meeting deletion."""
        # Create meeting
        create_response = client.post("/api/v1/meetings/", json=sample_meeting_data)
        meeting_id = create_response.json()["id"]
        
        # Delete meeting
        response = client.delete(f"/api/v1/meetings/{meeting_id}")
        
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/meetings/{meeting_id}")
        assert get_response.status_code == 404
    
    def test_delete_meeting_not_found(self, client: TestClient):
        """Test deleting a non-existent meeting."""
        response = client.delete("/api/v1/meetings/99999")
        
        assert response.status_code == 404
    
    def test_meeting_url_validation(self, client: TestClient, sample_meeting_data):
        """Test that meeting URL validation works correctly."""
        # Test valid URLs
        valid_urls = [
            "https://meet.google.com/abc-defg-hij",
            "https://teams.microsoft.com/l/meetup-join/...",
            "https://zoom.us/j/123456789",
            "https://example.com/meeting"
        ]
        
        for url in valid_urls:
            meeting_data = sample_meeting_data.copy()
            meeting_data["meeting_url"] = url
            meeting_data["title"] = f"Meeting for {url}"
            
            response = client.post("/api/v1/meetings/", json=meeting_data)
            assert response.status_code == 201, f"Failed for URL: {url}"
    
    def test_platform_enum_validation(self, client: TestClient, sample_meeting_data):
        """Test platform enum validation."""
        # Valid platforms
        valid_platforms = ["google_meet", "teams", "zoom"]
        
        for platform in valid_platforms:
            meeting_data = sample_meeting_data.copy()
            meeting_data["platform"] = platform
            meeting_data["title"] = f"Meeting for {platform}"
            meeting_data["meeting_url"] = f"https://example.com/{platform}"
            
            response = client.post("/api/v1/meetings/", json=meeting_data)
            assert response.status_code == 201
        
        # Invalid platform
        invalid_data = sample_meeting_data.copy()
        invalid_data["platform"] = "invalid_platform"
        
        response = client.post("/api/v1/meetings/", json=invalid_data)
        assert response.status_code == 422