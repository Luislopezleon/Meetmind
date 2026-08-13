import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import (
    Meeting, TranscriptChunk, ActionItem, Decision, 
    Risk, OpenQuestion, MeetingSummary
)


class TestMeetingModel:
    """Test Meeting model functionality."""
    
    def test_create_meeting(self, db_session: Session):
        """Test creating a basic meeting."""
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test",
            platform="google_meet",
            scheduled_at=datetime.now(timezone.utc)
        )
        
        db_session.add(meeting)
        db_session.commit()
        db_session.refresh(meeting)
        
        assert meeting.id is not None
        assert meeting.title == "Test Meeting"
        assert meeting.platform == "google_meet"
        assert meeting.status == "scheduled"  # Default value
        assert meeting.created_at is not None
        assert meeting.participants == []  # Default empty list
    
    def test_meeting_relationships(self, db_session: Session):
        """Test that meeting relationships work properly."""
        # Create meeting
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test",
            platform="google_meet",
            scheduled_at=datetime.now(timezone.utc)
        )
        db_session.add(meeting)
        db_session.commit()
        db_session.refresh(meeting)
        
        # Create related transcript chunk
        transcript = TranscriptChunk(
            meeting_id=meeting.id,
            text="Hello world",
            speaker_name="John",
            confidence=0.95
        )
        db_session.add(transcript)
        
        # Create related action item
        action_item = ActionItem(
            meeting_id=meeting.id,
            task="Complete the report",
            assignee="Jane",
            priority="high"
        )
        db_session.add(action_item)
        
        db_session.commit()
        
        # Test relationships
        assert len(meeting.transcripts) == 1
        assert len(meeting.action_items) == 1
        assert meeting.transcripts[0].text == "Hello world"
        assert meeting.action_items[0].task == "Complete the report"


class TestTranscriptChunkModel:
    """Test TranscriptChunk model functionality."""
    
    def test_create_transcript_chunk(self, db_session: Session):
        """Test creating a transcript chunk."""
        # First create a meeting
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test", 
            platform="google_meet",
            scheduled_at=datetime.now(timezone.utc)
        )
        db_session.add(meeting)
        db_session.commit()
        
        # Create transcript chunk
        chunk = TranscriptChunk(
            meeting_id=meeting.id,
            text="This is a test transcript",
            speaker_name="John Doe",
            speaker_id="speaker_123",
            confidence=0.92,
            start_time=10.5,
            end_time=15.8
        )
        
        db_session.add(chunk)
        db_session.commit()
        db_session.refresh(chunk)
        
        assert chunk.id is not None
        assert chunk.text == "This is a test transcript"
        assert chunk.speaker_name == "John Doe"
        assert chunk.confidence == 0.92
        assert chunk.processed_by_agent is False  # Default
        assert chunk.timestamp is not None
    
    def test_transcript_meeting_relationship(self, db_session: Session):
        """Test transcript to meeting relationship."""
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test",
            platform="google_meet", 
            scheduled_at=datetime.now(timezone.utc)
        )
        db_session.add(meeting)
        db_session.commit()
        
        chunk = TranscriptChunk(
            meeting_id=meeting.id,
            text="Test text",
            speaker_name="Speaker"
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Test back-reference
        assert chunk.meeting.title == "Test Meeting"


class TestActionItemModel:
    """Test ActionItem model functionality."""
    
    def test_create_action_item(self, db_session: Session):
        """Test creating an action item."""
        # Create meeting first
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test",
            platform="google_meet",
            scheduled_at=datetime.now(timezone.utc)
        )
        db_session.add(meeting)
        db_session.commit()
        
        # Create action item
        action_item = ActionItem(
            meeting_id=meeting.id,
            task="Send weekly report",
            assignee="Alice Johnson",
            deadline="next Friday",
            priority="medium",
            confidence_score=0.89,
            source_transcript_ids=[1, 2, 3]
        )
        
        db_session.add(action_item)
        db_session.commit()
        db_session.refresh(action_item)
        
        assert action_item.id is not None
        assert action_item.task == "Send weekly report"
        assert action_item.assignee == "Alice Johnson"
        assert action_item.priority == "medium"
        assert action_item.status == "open"  # Default
        assert action_item.confidence_score == 0.89
        assert action_item.source_transcript_ids == [1, 2, 3]
        assert action_item.detected_at is not None


class TestDecisionModel:
    """Test Decision model functionality."""
    
    def test_create_decision(self, db_session: Session):
        """Test creating a decision."""
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test",
            platform="google_meet",
            scheduled_at=datetime.now(timezone.utc)
        )
        db_session.add(meeting)
        db_session.commit()
        
        decision = Decision(
            meeting_id=meeting.id,
            decision="We will use React for the frontend",
            context="After evaluating Vue, Angular and React",
            impact="high",
            decision_maker="Technical Lead",
            stakeholders=["Dev Team", "Product Manager"],
            confidence_score=0.95
        )
        
        db_session.add(decision)
        db_session.commit()
        db_session.refresh(decision)
        
        assert decision.id is not None
        assert decision.decision == "We will use React for the frontend"
        assert decision.impact == "high"
        assert decision.stakeholders == ["Dev Team", "Product Manager"]
        assert decision.detected_at is not None


class TestModelCascade:
    """Test cascade delete behavior."""
    
    def test_meeting_cascade_delete(self, db_session: Session):
        """Test that deleting a meeting cascades to related records."""
        # Create meeting with related records
        meeting = Meeting(
            title="Test Meeting",
            meeting_url="https://meet.google.com/test",
            platform="google_meet",
            scheduled_at=datetime.now(timezone.utc)
        )
        db_session.add(meeting)
        db_session.commit()
        
        # Add related records
        transcript = TranscriptChunk(
            meeting_id=meeting.id,
            text="Test",
            speaker_name="Speaker"
        )
        action_item = ActionItem(
            meeting_id=meeting.id,
            task="Test task",
            assignee="Assignee"
        )
        
        db_session.add_all([transcript, action_item])
        db_session.commit()
        
        # Verify records exist
        assert db_session.query(TranscriptChunk).count() == 1
        assert db_session.query(ActionItem).count() == 1
        
        # Delete meeting
        db_session.delete(meeting)
        db_session.commit()
        
        # Verify cascade delete worked
        assert db_session.query(Meeting).count() == 0
        assert db_session.query(TranscriptChunk).count() == 0
        assert db_session.query(ActionItem).count() == 0