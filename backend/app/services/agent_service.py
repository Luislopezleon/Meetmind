"""
AgentService - Orchestrates the meeting intelligence agent.

Triggers the LangGraph agent on meeting transcripts and persists
the detected insights (action items, decisions, risks, questions, summary)
into the database.
"""

from typing import List, Optional
from loguru import logger
from sqlalchemy.orm import Session

from app.models import (
    Meeting, TranscriptChunk, ActionItem, Decision,
    Risk, OpenQuestion, MeetingSummary
)
from app.agents.meeting_agent import analyze_meeting
from app.db.redis import redis_manager


async def run_agent_on_meeting(meeting_id: int, db: Session) -> dict:
    """
    Run the full meeting intelligence agent on a completed meeting.
    
    Steps:
    1. Load all transcript chunks from DB
    2. Run the LangGraph agent
    3. Persist detected insights to DB
    4. Publish insights to Redis for real-time clients
    
    Args:
        meeting_id: ID of the meeting to analyze
        db: Database session
        
    Returns:
        Dict with counts of detected insights
    """
    # Load meeting
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        logger.error(f"Meeting {meeting_id} not found")
        return {"error": "Meeting not found"}
    
    # Load transcript chunks ordered by time
    chunks = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.meeting_id == meeting_id)
        .order_by(TranscriptChunk.start_time)
        .all()
    )
    
    if not chunks:
        logger.warning(f"No transcript chunks for meeting {meeting_id}")
        return {"error": "No transcript available"}
    
    # Format transcript for the agent
    transcript = [
        {
            "speaker": chunk.speaker_name or "Unknown",
            "text": chunk.text,
            "start_time": chunk.start_time or 0,
            "end_time": chunk.end_time or 0,
        }
        for chunk in chunks
    ]
    
    # Get participants
    participants = meeting.participants or []
    if not participants:
        # Extract from transcript
        participants = list(set(
            chunk.speaker_name for chunk in chunks
            if chunk.speaker_name and chunk.speaker_name != "Unknown"
        ))
    
    logger.info(f"Running agent on meeting {meeting_id}: {len(chunks)} chunks, {len(participants)} participants")
    
    # Run the agent
    result = await analyze_meeting(
        meeting_id=meeting_id,
        transcript=transcript,
        participants=participants,
    )
    
    # Persist results
    counts = await _persist_insights(meeting, result, db)
    
    # Publish insights to Redis
    await _publish_insights(meeting_id, result)
    
    # Mark chunks as processed
    for chunk in chunks:
        chunk.processed_by_agent = True
    db.commit()
    
    logger.info(
        f"Agent completed for meeting {meeting_id}: "
        f"{counts['action_items']} actions, {counts['decisions']} decisions, "
        f"{counts['risks']} risks, {counts['questions']} questions, "
        f"summary: {'yes' if counts['summary'] else 'no'}"
    )
    
    return counts


async def _persist_insights(meeting: Meeting, result: dict, db: Session) -> dict:
    """Persist agent results to the database."""
    counts = {"action_items": 0, "decisions": 0, "risks": 0, "questions": 0, "summary": False}
    
    # Action Items
    for item in result.get("action_items", []):
        action = ActionItem(
            meeting_id=meeting.id,
            task=item["task"],
            assignee=item.get("assignee"),
            deadline=item.get("deadline"),
            priority=item.get("priority", "medium"),
            confidence_score=item.get("confidence", 0.0),
        )
        db.add(action)
        counts["action_items"] += 1
    
    # Decisions
    for item in result.get("decisions", []):
        decision = Decision(
            meeting_id=meeting.id,
            decision=item["decision"],
            context=item.get("context"),
            impact=item.get("impact", "medium"),
            decision_maker=item.get("decision_maker"),
            confidence_score=item.get("confidence", 0.0),
        )
        db.add(decision)
        counts["decisions"] += 1
    
    # Risks
    for item in result.get("risks", []):
        risk = Risk(
            meeting_id=meeting.id,
            risk_description=item["description"],
            category=item.get("category"),
            severity=item.get("severity", "medium"),
            mitigation_suggested=item.get("mitigation"),
            confidence_score=item.get("confidence", 0.0),
        )
        db.add(risk)
        counts["risks"] += 1
    
    # Open Questions
    for item in result.get("questions", []):
        question = OpenQuestion(
            meeting_id=meeting.id,
            question=item["question"],
            context=item.get("context"),
            asked_by=item.get("asked_by"),
            assigned_to=item.get("assigned_to"),
            confidence_score=item.get("confidence", 0.0),
        )
        db.add(question)
        counts["questions"] += 1
    
    # Summary
    if result.get("summary"):
        summary = MeetingSummary(
            meeting_id=meeting.id,
            executive_summary=result["summary"],
            key_topics=[],  # Could extract from summary in future
            generated_by="gemini-3.5-flash",
            word_count=len(result["summary"].split()),
        )
        db.add(summary)
        counts["summary"] = True
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error persisting insights: {e}")
    
    return counts


async def _publish_insights(meeting_id: int, result: dict):
    """Publish detected insights to Redis for WebSocket clients."""
    try:
        # Publish each action item
        for item in result.get("action_items", []):
            await redis_manager.publish(
                f"insights:{meeting_id}",
                {"insight_type": "action_item", "data": item}
            )
        
        # Publish each decision
        for item in result.get("decisions", []):
            await redis_manager.publish(
                f"insights:{meeting_id}",
                {"insight_type": "decision", "data": item}
            )
        
        # Publish each risk
        for item in result.get("risks", []):
            await redis_manager.publish(
                f"insights:{meeting_id}",
                {"insight_type": "risk", "data": item}
            )
        
        # Publish each question
        for item in result.get("questions", []):
            await redis_manager.publish(
                f"insights:{meeting_id}",
                {"insight_type": "question", "data": item}
            )
        
        # Publish summary availability
        if result.get("summary"):
            await redis_manager.publish(
                f"meeting:{meeting_id}:status",
                {"status": "analysis_complete", "has_summary": True}
            )
    except Exception as e:
        logger.warning(f"Error publishing insights to Redis: {e}")
