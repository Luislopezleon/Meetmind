"""
RecallService - Integración con Recall.ai API para bots de reuniones.

Este servicio maneja:
- Creación de bots para unirse a reuniones
- Gestión del estado de los bots
- Recuperación de grabaciones y transcripciones
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from app.core.config import settings
from app.schemas import MeetingPlatform


class RecallServiceError(Exception):
    """Excepción base para errores del servicio Recall.ai"""
    pass


class RecallService:
    """Servicio para interactuar con la API de Recall.ai"""
    
    def __init__(self):
        self.api_key = settings.recall_ai_api_key
        self.region = settings.recall_region
        self.base_url = f"https://{self.region}.recall.ai/api/v1"
        
        if not self.api_key:
            logger.warning("RECALL_AI_API_KEY not configured. RecallService will not work.")
        
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test connection to Recall.ai API"""
        if not self.api_key:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/bot",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error testing Recall.ai connection: {e}")
            return False
    
    async def create_bot(
        self, 
        meeting_url: str,
        meeting_id: int,
        bot_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a bot to join a meeting.
        
        Args:
            meeting_url: URL of the meeting (Google Meet, Teams, Zoom)
            meeting_id: Internal meeting ID for tracking
            bot_name: Custom name for the bot (optional)
        
        Returns:
            Dict with bot information including bot_id
        """
        if not self.api_key:
            raise RecallServiceError("RECALL_AI_API_KEY not configured")
        
        # Generate bot name if not provided
        if not bot_name:
            bot_name = f"MeetMind Bot - Meeting {meeting_id}"
        
        payload = {
            "meeting_url": meeting_url,
            "bot_name": bot_name,
            "recording_config": {
                "transcript": {
                    "provider": {
                        "recallai_streaming": {}
                    }
                }
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/bot",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    bot_data = response.json()
                    logger.info(f"Bot created successfully: {bot_data['id']}")
                    return bot_data
                else:
                    error_msg = f"Failed to create bot: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise RecallServiceError(error_msg)
                    
        except httpx.RequestError as e:
            error_msg = f"Request error creating bot: {e}"
            logger.error(error_msg)
            raise RecallServiceError(error_msg)
    
    async def get_bot_status(self, bot_id: str) -> Dict[str, Any]:
        """
        Get current status of a bot.
        
        Args:
            bot_id: Recall.ai bot ID
            
        Returns:
            Dict with bot status and information
        """
        if not self.api_key:
            raise RecallServiceError("RECALL_AI_API_KEY not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/bot/{bot_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = f"Failed to get bot status: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise RecallServiceError(error_msg)
                    
        except httpx.RequestError as e:
            error_msg = f"Request error getting bot status: {e}"
            logger.error(error_msg)
            raise RecallServiceError(error_msg)
    
    async def get_bot_transcript(self, bot_id: str) -> List[Dict[str, Any]]:
        """
        Get transcript for a bot via the recording's transcript media shortcut.
        
        Args:
            bot_id: Recall.ai bot ID
            
        Returns:
            List of transcript segments with speaker information
        """
        if not self.api_key:
            raise RecallServiceError("RECALL_AI_API_KEY not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                # First get bot info to find recordings
                bot_info = await self.get_bot_status(bot_id)
                recordings = bot_info.get("recordings", [])
                
                if not recordings:
                    logger.info(f"No recordings found for bot {bot_id}")
                    return []
                
                # Get transcript from first recording's media shortcuts
                recording = recordings[0]
                media_shortcuts = recording.get("media_shortcuts", {})
                transcript_info = media_shortcuts.get("transcript", {})
                transcript_data = transcript_info.get("data", {})
                download_url = transcript_data.get("download_url")
                
                if not download_url:
                    logger.info(f"No transcript download URL for bot {bot_id}")
                    return []
                
                # Download the transcript
                response = await client.get(download_url, timeout=30.0)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = f"Failed to download transcript: {response.status_code}"
                    logger.error(error_msg)
                    raise RecallServiceError(error_msg)
                    
        except RecallServiceError:
            raise
        except Exception as e:
            error_msg = f"Error getting transcript: {e}"
            logger.error(error_msg)
            raise RecallServiceError(error_msg)
    
    async def delete_bot(self, bot_id: str) -> bool:
        """
        Delete a bot and its data.
        
        Args:
            bot_id: Recall.ai bot ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            raise RecallServiceError("RECALL_AI_API_KEY not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/bot/{bot_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 204:
                    logger.info(f"Bot {bot_id} deleted successfully")
                    return True
                else:
                    logger.error(f"Failed to delete bot: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Request error deleting bot: {e}")
            return False
    
    def get_current_status(self, status_changes: List[Dict[str, Any]]) -> str:
        """
        Extract current status from Recall.ai status_changes array.
        
        Args:
            status_changes: Array from Recall.ai bot response
            
        Returns:
            Current status code
        """
        if not status_changes:
            return "unknown"
        
        # Status changes are ordered by created_at, latest is current
        latest_status = status_changes[-1]
        return latest_status.get("code", "unknown")
    
    def map_platform_to_recall(self, platform: MeetingPlatform) -> str:
        """
        Map our platform enum to what Recall.ai expects.
        
        Args:
            platform: Our MeetingPlatform enum
            
        Returns:
            Platform string for Recall.ai (though they auto-detect)
        """
        mapping = {
            MeetingPlatform.GOOGLE_MEET: "google_meet",
            MeetingPlatform.TEAMS: "teams", 
            MeetingPlatform.ZOOM: "zoom"
        }
        return mapping.get(platform, "unknown")


# Global service instance
recall_service = RecallService()


# Status code mappings from Recall.ai to our system
RECALL_STATUS_MAPPING = {
    "ready": "scheduled",
    "joining_call": "connecting", 
    "in_waiting_room": "waiting",
    "in_call_not_recording": "connected",
    "in_call_recording": "in_progress",
    "call_ended": "ended",
    "done": "completed",
    "error": "failed"
}