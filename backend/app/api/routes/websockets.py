from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio

import redis.asyncio as aioredis
from loguru import logger

from app.db.database import get_db
from app.db.redis import redis_manager
from app.models import Meeting
from app.schemas import WebSocketMessage
from app.core.config import settings

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, meeting_id: int):
        """Accept a new WebSocket connection for a meeting."""
        await websocket.accept()
        
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = []
        
        self.active_connections[meeting_id].append(websocket)
        logger.info(f"WebSocket connected for meeting {meeting_id}. Total: {len(self.active_connections[meeting_id])}")
    
    def disconnect(self, websocket: WebSocket, meeting_id: int):
        """Remove a WebSocket connection."""
        if meeting_id in self.active_connections:
            if websocket in self.active_connections[meeting_id]:
                self.active_connections[meeting_id].remove(websocket)
                logger.info(f"WebSocket disconnected from meeting {meeting_id}. Remaining: {len(self.active_connections[meeting_id])}")
                
                if not self.active_connections[meeting_id]:
                    del self.active_connections[meeting_id]
    
    async def send_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception:
            pass  # Client likely disconnected
    
    async def broadcast_to_meeting(self, message: str, meeting_id: int):
        """Broadcast a message to all connections for a meeting."""
        if meeting_id not in self.active_connections:
            return
            
        disconnected = []
        for websocket in self.active_connections[meeting_id]:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(websocket)
        
        for websocket in disconnected:
            self.disconnect(websocket, meeting_id)


# Global connection manager
manager = ConnectionManager()


async def redis_listener(websocket: WebSocket, meeting_id: int):
    """
    Subscribe to Redis pub/sub channels for a meeting and forward messages
    to the WebSocket client.
    
    Channels:
    - transcript:{meeting_id}  -> new transcript chunks
    - insights:{meeting_id}    -> detected action items, decisions, risks
    - meeting:{meeting_id}:status -> bot/meeting status changes
    """
    channels = [
        f"transcript:{meeting_id}",
        f"insights:{meeting_id}",
        f"meeting:{meeting_id}:status",
    ]
    
    # Create a dedicated Redis connection for this subscription
    try:
        sub_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        pubsub = sub_client.pubsub()
        await pubsub.subscribe(*channels)
        logger.info(f"Redis subscribed to channels for meeting {meeting_id}")
    except Exception as e:
        logger.error(f"Failed to subscribe to Redis for meeting {meeting_id}: {e}")
        return
    
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            
            channel = message["channel"]
            data = message["data"]
            
            # Parse the data (stored as JSON string)
            try:
                payload = json.loads(data) if isinstance(data, str) else data
            except json.JSONDecodeError:
                payload = {"raw": data}
            
            # Determine message type from channel
            if channel.startswith("transcript:"):
                ws_message = WebSocketMessage(
                    type="transcript_chunk",
                    data=payload
                )
            elif channel.startswith("insights:"):
                ws_message = WebSocketMessage(
                    type="insight_detected",
                    data=payload
                )
            elif "status" in channel:
                ws_message = WebSocketMessage(
                    type="status_update",
                    data=payload
                )
            else:
                ws_message = WebSocketMessage(
                    type="unknown",
                    data=payload
                )
            
            # Send to the WebSocket client
            try:
                await websocket.send_text(ws_message.model_dump_json())
            except Exception:
                # Client disconnected
                break
                
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Redis listener error for meeting {meeting_id}: {e}")
    finally:
        await pubsub.unsubscribe(*channels)
        await pubsub.aclose()
        await sub_client.aclose()
        logger.info(f"Redis unsubscribed from channels for meeting {meeting_id}")


@router.websocket("/{meeting_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    meeting_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time meeting updates.
    
    Clients connect to /ws/{meeting_id} to receive:
    - Real-time transcript chunks (from Redis channel transcript:{id})
    - Detected insights (from Redis channel insights:{id})
    - Meeting status updates (from Redis channel meeting:{id}:status)
    """
    
    # Verify meeting exists
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        await websocket.close(code=4004, reason="Meeting not found")
        return
    
    # Accept connection
    await manager.connect(websocket, meeting_id)
    
    # Send initial meeting data
    initial_message = WebSocketMessage(
        type="meeting_connected",
        data={
            "meeting_id": meeting_id,
            "title": meeting.title,
            "status": meeting.status,
            "message": "Connected to meeting feed"
        }
    )
    await manager.send_message(initial_message.model_dump_json(), websocket)
    
    # Start Redis listener as a background task
    listener_task = asyncio.create_task(redis_listener(websocket, meeting_id))
    
    try:
        # Main loop: handle client messages (ping/pong, commands)
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "ping":
                    response = WebSocketMessage(
                        type="pong",
                        data={"message": "pong"}
                    )
                    await manager.send_message(response.model_dump_json(), websocket)
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.error(f"WebSocket loop error: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        # Cancel the Redis listener
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass
        
        manager.disconnect(websocket, meeting_id)


# --- Helper functions for broadcasting from other parts of the app ---

async def broadcast_transcript_chunk(meeting_id: int, transcript_data: dict):
    """Broadcast new transcript chunk to all connected clients via Redis."""
    await redis_manager.publish(f"transcript:{meeting_id}", transcript_data)


async def broadcast_insight(meeting_id: int, insight_type: str, insight_data: dict):
    """Broadcast new insight to all connected clients via Redis."""
    await redis_manager.publish(
        f"insights:{meeting_id}",
        {"insight_type": insight_type, "data": insight_data}
    )


async def broadcast_status_update(meeting_id: int, status: str, details: dict = None):
    """Broadcast meeting status update to all connected clients via Redis."""
    await redis_manager.publish(
        f"meeting:{meeting_id}:status",
        {"status": status, "details": details or {}}
    )
