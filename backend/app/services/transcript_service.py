"""
TranscriptService - Fetches and stores transcription from Recall.ai.

Handles the real Recall.ai transcript format:
- participant: {id, name, is_host, platform, email, extra_data}
- words: [{text, start_timestamp: {relative, absolute}, end_timestamp: {relative, absolute}}]
- language_code: "es", "en", etc.
"""

from typing import List, Dict, Any
from loguru import logger
from sqlalchemy.orm import Session

from app.models import Meeting, TranscriptChunk
from app.services.recall_service import recall_service, RecallServiceError
from app.db.redis import redis_manager


async def fetch_and_store_transcript(meeting: Meeting, db: Session) -> int:
    """
    Fetch transcript from Recall.ai and store chunks in database.
    
    Args:
        meeting: Meeting model instance with recall_bot_id
        db: Database session
        
    Returns:
        Number of transcript chunks stored
    """
    if not meeting.recall_bot_id:
        logger.warning(f"Meeting {meeting.id} has no bot_id, cannot fetch transcript")
        return 0
    
    try:
        transcript_data = await recall_service.get_bot_transcript(meeting.recall_bot_id)
    except RecallServiceError as e:
        logger.error(f"Failed to fetch transcript for meeting {meeting.id}: {e}")
        return 0
    
    if not transcript_data:
        logger.info(f"No transcript data for meeting {meeting.id}")
        return 0
    
    chunks_stored = 0
    
    for segment in transcript_data:
        # Parse participant info
        participant = segment.get("participant", {})
        speaker_name = participant.get("name", "Unknown")
        speaker_id = str(participant.get("id", ""))
        
        # Parse words
        words = segment.get("words", [])
        if not words:
            continue
        
        # Combine words into text
        text = " ".join([w.get("text", "") for w in words])
        if not text.strip():
            continue
        
        # Get timing from first and last word
        first_word = words[0]
        last_word = words[-1]
        
        start_time = first_word.get("start_timestamp", {}).get("relative", 0)
        end_time = last_word.get("end_timestamp", {}).get("relative", 0)
        
        # Check for duplicates
        existing = db.query(TranscriptChunk).filter(
            TranscriptChunk.meeting_id == meeting.id,
            TranscriptChunk.speaker_id == speaker_id,
            TranscriptChunk.start_time == start_time
        ).first()
        
        if existing:
            continue
        
        # Create transcript chunk
        chunk = TranscriptChunk(
            meeting_id=meeting.id,
            text=text,
            speaker_name=speaker_name,
            speaker_id=speaker_id,
            start_time=start_time,
            end_time=end_time,
            confidence=0.95,  # Recall.ai doesn't provide per-segment confidence
        )
        
        db.add(chunk)
        chunks_stored += 1
        
        # Publish to Redis for real-time clients (if any are still connected)
        try:
            await redis_manager.publish(
                f"transcript:{meeting.id}",
                {
                    "text": text,
                    "speaker": speaker_name,
                    "speaker_id": speaker_id,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to publish transcript chunk to Redis: {e}")
    
    # Update participants from transcript if not already set
    if transcript_data and not meeting.participants:
        participant_names = list(set(
            seg.get("participant", {}).get("name", "")
            for seg in transcript_data
            if seg.get("participant", {}).get("name")
        ))
        if participant_names:
            meeting.participants = participant_names
    
    try:
        db.commit()
        logger.info(f"Stored {chunks_stored} transcript chunks for meeting {meeting.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing transcript chunks: {e}")
        return 0
    
    return chunks_stored
