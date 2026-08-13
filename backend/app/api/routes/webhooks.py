from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.db.database import get_db
from app.db.redis import redis_manager
from app.models import Meeting, TranscriptChunk
from app.core.config import settings
from app.services.transcript_service import fetch_and_store_transcript
from app.services.agent_service import run_agent_on_meeting

router = APIRouter()


async def verify_recall_webhook(request: Request) -> dict:
    """
    Verify Recall.ai webhook signature using Svix.
    
    Recall.ai delivers webhooks via Svix. The signing secret is configured
    in the Recall dashboard when you create a webhook endpoint.
    """
    payload = await request.body()
    headers = dict(request.headers)
    
    # Skip verification in development if no secret configured
    if not settings.recall_webhook_secret:
        if settings.environment == "development":
            logger.warning("Webhook signature verification skipped (no secret configured)")
            import json
            return json.loads(payload)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Webhook secret not configured"
            )
    
    try:
        from svix.webhooks import Webhook, WebhookVerificationError
        
        wh = Webhook(settings.recall_webhook_secret)
        msg = wh.verify(payload, headers)
        return msg
    except WebhookVerificationError:
        logger.error("Webhook signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        logger.error(f"Error verifying webhook: {e}")
        # In development, still process the webhook
        if settings.environment == "development":
            import json
            return json.loads(payload)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook verification error"
        )


@router.post("/recall", status_code=status.HTTP_204_NO_CONTENT)
async def handle_recall_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle webhook events from Recall.ai (delivered via Svix).
    
    Events handled:
    - bot.joining_call: Bot is connecting to the meeting
    - bot.in_waiting_room: Bot is in waiting room
    - bot.in_call_not_recording: Bot joined but not recording yet
    - bot.in_call_recording: Bot is recording
    - bot.call_ended: Meeting ended
    - bot.done: Bot finished, recording available
    - bot.fatal: Bot encountered an error
    """
    # Verify and parse webhook payload
    payload = await verify_recall_webhook(request)
    
    # Extract event info (Recall.ai webhook format)
    event_type = payload.get("event")
    data = payload.get("data", {})
    bot_info = data.get("bot", {})
    bot_id = bot_info.get("id")
    event_data = data.get("data", {})
    
    if not event_type or not bot_id:
        logger.warning(f"Webhook missing event or bot_id: {payload}")
        return
    
    logger.info(f"Webhook received: {event_type} for bot {bot_id}")
    
    # Find the meeting associated with this bot
    meeting = db.query(Meeting).filter(
        Meeting.recall_bot_id == bot_id
    ).first()
    
    if not meeting:
        logger.warning(f"Webhook for unknown bot_id: {bot_id}")
        return
    
    # Map Recall.ai event to our status
    status_code = event_data.get("code", "")
    sub_code = event_data.get("sub_code")
    updated_at = event_data.get("updated_at")
    
    # Handle different event types
    if event_type == "bot.joining_call":
        meeting.status = "connecting"
        
    elif event_type == "bot.in_waiting_room":
        meeting.status = "waiting"
        
    elif event_type == "bot.in_call_not_recording":
        meeting.status = "connected"
        
    elif event_type == "bot.in_call_recording":
        meeting.status = "in_progress"
        if not meeting.started_at:
            meeting.started_at = datetime.utcnow()
        
    elif event_type == "bot.call_ended":
        meeting.status = "ended"
        meeting.ended_at = datetime.utcnow()
        
    elif event_type == "bot.done":
        meeting.status = "completed"
        if not meeting.ended_at:
            meeting.ended_at = datetime.utcnow()
        # Fetch transcript and run agent
        try:
            db.commit()  # Commit status change first
            chunks = await fetch_and_store_transcript(meeting, db)
            logger.info(f"Fetched {chunks} transcript chunks for meeting {meeting.id}")
            
            # Run the intelligence agent on the transcript
            if chunks > 0:
                agent_result = await run_agent_on_meeting(meeting.id, db)
                logger.info(f"Agent analysis complete for meeting {meeting.id}: {agent_result}")
        except Exception as e:
            logger.error(f"Error processing bot.done for meeting {meeting.id}: {e}")
        
    elif event_type == "bot.fatal":
        meeting.status = "failed"
        logger.error(f"Bot fatal error for meeting {meeting.id}: {sub_code}")
    
    else:
        logger.info(f"Unhandled event type: {event_type}")
    
    try:
        db.commit()
        logger.info(f"Meeting {meeting.id} status updated to: {meeting.status}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating meeting status: {e}")
        return
    
    # Publish status update via Redis for WebSocket clients
    try:
        await redis_manager.publish(
            f"meeting:{meeting.id}:status",
            {
                "event": event_type,
                "bot_id": bot_id,
                "meeting_id": meeting.id,
                "status": meeting.status,
                "sub_code": sub_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error publishing to Redis: {e}")
