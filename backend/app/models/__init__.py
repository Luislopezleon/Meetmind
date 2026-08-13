from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Meeting(Base):
    """Model for storing meeting information."""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    meeting_url = Column(String(512), nullable=False)
    platform = Column(String(50), nullable=False)  # google_meet, teams, zoom
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, failed
    
    # Recall.ai bot information
    recall_bot_id = Column(String(255), unique=True, index=True)
    recall_meeting_id = Column(String(255), unique=True, index=True)
    
    # Meeting metadata
    participants = Column(JSON, default=list)  # List of participant names
    duration_minutes = Column(Integer)
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transcripts = relationship("TranscriptChunk", back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="meeting", cascade="all, delete-orphan")
    open_questions = relationship("OpenQuestion", back_populates="meeting", cascade="all, delete-orphan")
    summary = relationship("MeetingSummary", back_populates="meeting", uselist=False)


class TranscriptChunk(Base):
    """Model for storing individual transcript chunks."""
    __tablename__ = "transcript_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Content
    text = Column(Text, nullable=False)
    speaker_name = Column(String(255))
    speaker_id = Column(String(255))
    confidence = Column(Float)  # Transcription confidence score
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    start_time = Column(Float)  # Seconds from meeting start
    end_time = Column(Float)    # Seconds from meeting start
    
    # Processing status
    processed_by_agent = Column(Boolean, default=False)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="transcripts")


class ActionItem(Base):
    """Model for storing detected action items."""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Content
    task = Column(Text, nullable=False)
    assignee = Column(String(255))
    deadline = Column(String(255))  # Natural language deadline
    priority = Column(String(50))   # low, medium, high
    status = Column(String(50), default="open")  # open, in_progress, completed
    
    # AI Detection metadata
    confidence_score = Column(Float)
    source_transcript_ids = Column(JSON)  # List of transcript chunk IDs that led to this detection
    
    # External sync
    jira_issue_id = Column(String(255))
    jira_issue_key = Column(String(255))
    notion_page_id = Column(String(255))
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    
    # Relationships
    meeting = relationship("Meeting", back_populates="action_items")


class Decision(Base):
    """Model for storing detected decisions."""
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Content
    decision = Column(Text, nullable=False)
    context = Column(Text)  # Additional context
    impact = Column(String(50))  # low, medium, high
    
    # People involved
    decision_maker = Column(String(255))
    stakeholders = Column(JSON)  # List of people affected
    
    # AI Detection metadata
    confidence_score = Column(Float)
    source_transcript_ids = Column(JSON)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="decisions")


class Risk(Base):
    """Model for storing detected risks and concerns."""
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Content
    risk_description = Column(Text, nullable=False)
    category = Column(String(100))  # technical, timeline, resource, etc.
    severity = Column(String(50))   # low, medium, high, critical
    mitigation_suggested = Column(Text)
    
    # AI Detection metadata
    confidence_score = Column(Float)
    source_transcript_ids = Column(JSON)
    
    # Status
    status = Column(String(50), default="identified")  # identified, mitigated, resolved
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="risks")


class OpenQuestion(Base):
    """Model for storing open questions that need follow-up."""
    __tablename__ = "open_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Content
    question = Column(Text, nullable=False)
    context = Column(Text)
    category = Column(String(100))  # clarification, decision_needed, research_required
    
    # People
    asked_by = Column(String(255))
    assigned_to = Column(String(255))
    
    # AI Detection metadata
    confidence_score = Column(Float)
    source_transcript_ids = Column(JSON)
    
    # Status
    status = Column(String(50), default="open")  # open, answered, resolved
    answer = Column(Text)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    meeting = relationship("Meeting", back_populates="open_questions")


class MeetingSummary(Base):
    """Model for storing AI-generated meeting summaries."""
    __tablename__ = "meeting_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Summary content
    executive_summary = Column(Text, nullable=False)
    key_topics = Column(JSON)  # List of main topics discussed
    next_steps = Column(Text)
    
    # Metadata
    generated_by = Column(String(100))  # AI model used
    word_count = Column(Integer)
    
    # External sync
    notion_page_id = Column(String(255))
    shared_links = Column(JSON)  # List of shared links
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="summary")