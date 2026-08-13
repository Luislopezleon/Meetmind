from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MeetingPlatform(str, Enum):
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"
    ZOOM = "zoom"


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    BOT_CREATED = "bot_created"
    BOT_FAILED = "bot_failed"
    CONNECTING = "connecting"
    WAITING = "waiting"
    CONNECTED = "connected"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
    COMPLETED = "completed"
    FAILED = "failed"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionItemStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# Meeting Schemas
class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    meeting_url: HttpUrl
    platform: MeetingPlatform
    scheduled_at: datetime
    participants: Optional[List[str]] = []


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[MeetingStatus] = None
    participants: Optional[List[str]] = None
    duration_minutes: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class MeetingResponse(BaseModel):
    id: int
    title: str
    meeting_url: str
    platform: MeetingPlatform
    status: MeetingStatus
    recall_bot_id: Optional[str]
    recall_meeting_id: Optional[str]
    participants: List[str]
    duration_minutes: Optional[int]
    scheduled_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Transcript Schemas
class TranscriptChunkCreate(BaseModel):
    meeting_id: int
    text: str
    speaker_name: Optional[str] = None
    speaker_id: Optional[str] = None
    confidence: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class TranscriptChunkResponse(BaseModel):
    id: int
    meeting_id: int
    text: str
    speaker_name: Optional[str]
    speaker_id: Optional[str]
    confidence: Optional[float]
    timestamp: datetime
    start_time: Optional[float]
    end_time: Optional[float]
    processed_by_agent: bool
    
    class Config:
        from_attributes = True


# Action Item Schemas
class ActionItemCreate(BaseModel):
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[Priority] = Priority.MEDIUM
    confidence_score: Optional[float] = None
    source_transcript_ids: Optional[List[int]] = []


class ActionItemUpdate(BaseModel):
    task: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[ActionItemStatus] = None
    due_date: Optional[datetime] = None


class ActionItemResponse(BaseModel):
    id: int
    meeting_id: int
    task: str
    assignee: Optional[str]
    deadline: Optional[str]
    priority: Priority
    status: ActionItemStatus
    confidence_score: Optional[float]
    source_transcript_ids: Optional[List[int]]
    jira_issue_id: Optional[str]
    jira_issue_key: Optional[str]
    notion_page_id: Optional[str]
    detected_at: datetime
    due_date: Optional[datetime]
    
    class Config:
        from_attributes = True


# Decision Schemas
class DecisionCreate(BaseModel):
    decision: str
    context: Optional[str] = None
    impact: Optional[Priority] = Priority.MEDIUM
    decision_maker: Optional[str] = None
    stakeholders: Optional[List[str]] = []
    confidence_score: Optional[float] = None
    source_transcript_ids: Optional[List[int]] = []


class DecisionResponse(BaseModel):
    id: int
    meeting_id: int
    decision: str
    context: Optional[str]
    impact: Priority
    decision_maker: Optional[str]
    stakeholders: List[str]
    confidence_score: Optional[float]
    source_transcript_ids: Optional[List[int]]
    detected_at: datetime
    
    class Config:
        from_attributes = True


# Risk Schemas
class RiskCreate(BaseModel):
    risk_description: str
    category: Optional[str] = None
    severity: Optional[Priority] = Priority.MEDIUM
    mitigation_suggested: Optional[str] = None
    confidence_score: Optional[float] = None
    source_transcript_ids: Optional[List[int]] = []


class RiskResponse(BaseModel):
    id: int
    meeting_id: int
    risk_description: str
    category: Optional[str]
    severity: Priority
    mitigation_suggested: Optional[str]
    confidence_score: Optional[float]
    source_transcript_ids: Optional[List[int]]
    status: str
    detected_at: datetime
    
    class Config:
        from_attributes = True


# Open Question Schemas
class OpenQuestionCreate(BaseModel):
    question: str
    context: Optional[str] = None
    category: Optional[str] = None
    asked_by: Optional[str] = None
    assigned_to: Optional[str] = None
    confidence_score: Optional[float] = None
    source_transcript_ids: Optional[List[int]] = []


class OpenQuestionResponse(BaseModel):
    id: int
    meeting_id: int
    question: str
    context: Optional[str]
    category: Optional[str]
    asked_by: Optional[str]
    assigned_to: Optional[str]
    confidence_score: Optional[float]
    source_transcript_ids: Optional[List[int]]
    status: str
    answer: Optional[str]
    detected_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Meeting Summary Schemas
class MeetingSummaryCreate(BaseModel):
    executive_summary: str
    key_topics: Optional[List[str]] = []
    next_steps: Optional[str] = None
    generated_by: Optional[str] = "gpt-4o-mini"
    word_count: Optional[int] = None


class MeetingSummaryResponse(BaseModel):
    id: int
    meeting_id: int
    executive_summary: str
    key_topics: List[str]
    next_steps: Optional[str]
    generated_by: str
    word_count: Optional[int]
    notion_page_id: Optional[str]
    shared_links: Optional[List[str]]
    generated_at: datetime
    
    class Config:
        from_attributes = True


# Webhook Schemas
class RecallWebhookEvent(BaseModel):
    event: str
    bot_id: str
    meeting_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


# WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check Schema
class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    services: Dict[str, str] = {}


# Error Response Schema
class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)