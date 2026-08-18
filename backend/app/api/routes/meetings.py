from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models import Meeting
from app.schemas import MeetingCreate, MeetingUpdate, MeetingResponse, ErrorResponse
from app.services.recall_service import recall_service, RecallServiceError

router = APIRouter()


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db)
) -> MeetingResponse:
    """
    Create a new meeting and automatically send a Recall.ai bot to join it.
    
    This endpoint:
    1. Creates a meeting record in our database
    2. Sends a bot to the meeting via Recall.ai
    3. Returns the meeting info with bot_id for tracking
    """
    try:
        # Create meeting instance first
        db_meeting = Meeting(
            title=meeting_data.title,
            meeting_url=str(meeting_data.meeting_url),
            platform=meeting_data.platform,
            scheduled_at=meeting_data.scheduled_at,
            participants=meeting_data.participants or [],
            status="scheduled"
        )
        
        # Save to database to get ID
        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        
        # Now create the Recall.ai bot
        try:
            bot_data = await recall_service.create_bot(
                meeting_url=str(meeting_data.meeting_url),
                meeting_id=db_meeting.id,
                bot_name=f"MeetMind Bot - {meeting_data.title}"
            )
            
            # Update meeting with bot information
            db_meeting.recall_bot_id = bot_data["id"] 
            db_meeting.status = "bot_created"
            
            # Store additional bot info if needed
            if "meeting_metadata" in bot_data:
                # Could store in a JSON field if we add one
                pass
            
            db.commit()
            db.refresh(db_meeting)
            
            print(f"✅ Meeting {db_meeting.id} created with bot {bot_data['id']}")
            
        except RecallServiceError as e:
            # Bot creation failed, but meeting exists
            db_meeting.status = "bot_failed"
            db.commit()
            
            # Don't fail the entire request, just log the error
            print(f"⚠️  Meeting {db_meeting.id} created but bot creation failed: {e}")
            # Could still return the meeting - user can retry bot creation later
        
        return MeetingResponse.model_validate(db_meeting)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create meeting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create meeting: {str(e)}"
        )


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
) -> MeetingResponse:
    """Get a specific meeting by ID."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with id {meeting_id} not found"
        )
    
    return MeetingResponse.model_validate(meeting)


@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[MeetingResponse]:
    """List all meetings with pagination."""
    meetings = db.query(Meeting).offset(skip).limit(limit).all()
    return [MeetingResponse.model_validate(meeting) for meeting in meetings]


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    db: Session = Depends(get_db)
) -> MeetingResponse:
    """Update an existing meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with id {meeting_id} not found"
        )
    
    # Update fields if provided
    update_data = meeting_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)
    
    # Update timestamp
    meeting.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(meeting)
        return MeetingResponse.model_validate(meeting)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update meeting: {str(e)}"
        )


@router.get("/{meeting_id}/bot-status")
async def get_meeting_bot_status(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get the current status of the Recall.ai bot for this meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with id {meeting_id} not found"
        )
    
    if not meeting.recall_bot_id:
        return {
            "meeting_id": meeting_id,
            "bot_status": "no_bot",
            "message": "No bot created for this meeting"
        }
    
    try:
        bot_data = await recall_service.get_bot_status(meeting.recall_bot_id)
        current_status = recall_service.get_current_status(bot_data.get("status_changes", []))
        
        return {
            "meeting_id": meeting_id,
            "bot_id": meeting.recall_bot_id,
            "bot_status": current_status,
            "meeting_status": meeting.status,
            "status_changes": bot_data.get("status_changes", []),
            "video_url": bot_data.get("video_url"),
            "participants": bot_data.get("meeting_participants", [])
        }
        
    except RecallServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bot status: {str(e)}"
        )


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Delete a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with id {meeting_id} not found"
        )
    
    try:
        db.delete(meeting)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete meeting: {str(e)}"
        )


# --- Data endpoints for meeting detail ---

from app.models import TranscriptChunk, ActionItem, Decision, Risk, OpenQuestion, MeetingSummary


@router.get("/{meeting_id}/transcript")
async def get_meeting_transcript(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get all transcript chunks for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    chunks = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.meeting_id == meeting_id)
        .order_by(TranscriptChunk.start_time)
        .all()
    )
    
    return [
        {
            "id": c.id,
            "text": c.text,
            "speaker": c.speaker_name or "Unknown",
            "start_time": c.start_time,
            "end_time": c.end_time,
        }
        for c in chunks
    ]


@router.get("/{meeting_id}/insights")
async def get_meeting_insights(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """Get all detected insights for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    action_items = db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).all()
    decisions = db.query(Decision).filter(Decision.meeting_id == meeting_id).all()
    risks = db.query(Risk).filter(Risk.meeting_id == meeting_id).all()
    questions = db.query(OpenQuestion).filter(OpenQuestion.meeting_id == meeting_id).all()
    summary = db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting_id).first()
    
    return {
        "action_items": [
            {
                "task": a.task,
                "assignee": a.assignee,
                "deadline": a.deadline,
                "priority": a.priority,
                "confidence": a.confidence_score,
            }
            for a in action_items
        ],
        "decisions": [
            {
                "decision": d.decision,
                "context": d.context,
                "impact": d.impact,
                "decision_maker": d.decision_maker,
                "confidence": d.confidence_score,
            }
            for d in decisions
        ],
        "risks": [
            {
                "description": r.risk_description,
                "category": r.category,
                "severity": r.severity,
                "mitigation": r.mitigation_suggested,
                "confidence": r.confidence_score,
            }
            for r in risks
        ],
        "questions": [
            {
                "question": q.question,
                "context": q.context,
                "asked_by": q.asked_by,
                "assigned_to": q.assigned_to,
                "confidence": q.confidence_score,
            }
            for q in questions
        ],
        "summary": summary.executive_summary if summary else None,
    }

from app.services.agent_service import run_agent_on_meeting


@router.post("/{meeting_id}/analyze")
async def analyze_meeting_endpoint(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually trigger the AI agent to analyze a meeting's transcript.
    
    This re-runs the full analysis pipeline:
    - Extracts action items, decisions, risks, and open questions
    - Generates an executive summary
    - Stores results in the database
    - Publishes insights to WebSocket clients
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check there's a transcript to analyze
    chunk_count = db.query(TranscriptChunk).filter(
        TranscriptChunk.meeting_id == meeting_id
    ).count()
    
    if chunk_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No transcript available to analyze"
        )
    
    # Clear previous insights (re-analysis)
    db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).delete()
    db.query(Decision).filter(Decision.meeting_id == meeting_id).delete()
    db.query(Risk).filter(Risk.meeting_id == meeting_id).delete()
    db.query(OpenQuestion).filter(OpenQuestion.meeting_id == meeting_id).delete()
    db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting_id).delete()
    db.commit()
    
    # Run agent
    result = await run_agent_on_meeting(meeting_id, db)
    
    return {
        "meeting_id": meeting_id,
        "status": "analysis_complete",
        "results": result,
    }


@router.get("/stats/overview")
async def get_meetings_stats(
    db: Session = Depends(get_db)
):
    """Get overview stats for the dashboard."""
    total_meetings = db.query(Meeting).count()
    completed = db.query(Meeting).filter(Meeting.status == "completed").count()
    active = db.query(Meeting).filter(Meeting.status.in_(["in_progress", "connecting", "waiting", "connected"])).count()
    total_action_items = db.query(ActionItem).count()
    total_decisions = db.query(Decision).count()
    total_risks = db.query(Risk).count()
    
    return {
        "meetings": {
            "total": total_meetings,
            "completed": completed,
            "active": active,
        },
        "insights": {
            "action_items": total_action_items,
            "decisions": total_decisions,
            "risks": total_risks,
        },
    }


@router.post("/{meeting_id}/fetch-and-analyze")
async def fetch_and_analyze_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetch transcript from Recall.ai and run the AI agent.
    
    Use this when webhooks are not configured — manually triggers
    the full pipeline: fetch transcript → store → analyze → persist insights.
    """
    from app.services.transcript_service import fetch_and_store_transcript
    
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.recall_bot_id:
        raise HTTPException(status_code=400, detail="No bot associated with this meeting")
    
    # Fetch transcript
    chunks = await fetch_and_store_transcript(meeting, db)
    
    if chunks == 0:
        raise HTTPException(status_code=400, detail="No transcript available (meeting may still be in progress)")
    
    # Update status
    meeting.status = "completed"
    db.commit()
    
    # Run agent
    result = await run_agent_on_meeting(meeting_id, db)
    
    return {
        "meeting_id": meeting_id,
        "transcript_chunks": chunks,
        "analysis": result,
    }
