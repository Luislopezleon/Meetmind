"""Agent state definition for the Meeting Intelligence Agent."""

from typing import TypedDict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TranscriptSegment:
    """A segment of transcript with speaker info."""
    text: str
    speaker: str
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class DetectedActionItem:
    """An action item detected by the agent."""
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    confidence: float = 0.0


@dataclass
class DetectedDecision:
    """A decision detected by the agent."""
    decision: str
    context: Optional[str] = None
    impact: str = "medium"  # low, medium, high
    decision_maker: Optional[str] = None
    confidence: float = 0.0


@dataclass
class DetectedRisk:
    """A risk detected by the agent."""
    description: str
    category: Optional[str] = None  # technical, timeline, resource, dependency
    severity: str = "medium"  # low, medium, high, critical
    mitigation: Optional[str] = None
    confidence: float = 0.0


@dataclass
class DetectedQuestion:
    """An open question detected by the agent."""
    question: str
    context: Optional[str] = None
    asked_by: Optional[str] = None
    assigned_to: Optional[str] = None
    confidence: float = 0.0


class AgentState(TypedDict):
    """State passed between nodes in the LangGraph agent."""
    
    # Input
    meeting_id: int
    transcript: List[dict]  # List of transcript segments
    
    # Detected insights
    action_items: List[dict]
    decisions: List[dict]
    risks: List[dict]
    questions: List[dict]
    
    # Summary (generated at end)
    summary: Optional[str]
    
    # Metadata
    language: str  # detected language of the meeting
    participants: List[str]
