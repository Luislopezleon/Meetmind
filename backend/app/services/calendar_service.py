"""
CalendarService - Fetches upcoming meetings from Google Calendar
and automatically sends bots to join them.

Uses Google Calendar API with service account or OAuth token.
Polls for upcoming meetings and creates MeetMind meetings + bots.
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from loguru import logger
from sqlalchemy.orm import Session

from app.models import Meeting
from app.models.integrations import IntegrationConfig
from app.services.recall_service import recall_service, RecallServiceError


class CalendarServiceError(Exception):
    """Exception for Calendar service errors."""
    pass


class CalendarService:
    """Service to interact with Google Calendar API."""
    
    CALENDAR_API = "https://www.googleapis.com/calendar/v3"
    
    def _get_config(self, db: Session) -> Optional[Dict[str, Any]]:
        """Get Google Calendar config from database."""
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.integration_type == "google_calendar",
            IntegrationConfig.enabled == True
        ).first()
        
        if not config:
            return None
        return config.config
    
    async def is_connected(self, db: Session) -> bool:
        """Check if Google Calendar is configured."""
        config = self._get_config(db)
        return config is not None and bool(config.get("access_token"))
    
    async def get_upcoming_meetings(
        self,
        db: Session,
        lookahead_minutes: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Fetch upcoming calendar events that have video conference links.
        
        Returns list of events with: {summary, start, meet_url, calendar_event_id}
        """
        config = self._get_config(db)
        if not config:
            return []
        
        access_token = config.get("access_token", "")
        calendar_id = config.get("calendar_id", "primary")
        
        if not access_token:
            return []
        
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(minutes=lookahead_minutes)).isoformat()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.CALENDAR_API}/calendars/{calendar_id}/events",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={
                        "timeMin": time_min,
                        "timeMax": time_max,
                        "singleEvents": "true",
                        "orderBy": "startTime",
                    },
                    timeout=10.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"Calendar API error: {response.status_code}")
                    return []
                
                events = response.json().get("items", [])
                
                # Filter to events with video conference (Meet/Teams/Zoom)
                meetings = []
                for event in events:
                    meet_url = self._extract_meet_url(event)
                    if meet_url:
                        meetings.append({
                            "summary": event.get("summary", "Untitled"),
                            "start": event.get("start", {}).get("dateTime", ""),
                            "meet_url": meet_url,
                            "calendar_event_id": event.get("id", ""),
                        })
                
                return meetings
                
        except httpx.RequestError as e:
            logger.error(f"Calendar request error: {e}")
            return []
    
    def _extract_meet_url(self, event: Dict) -> Optional[str]:
        """Extract video meeting URL from a calendar event."""
        # Google Meet via conferenceData
        conference = event.get("conferenceData", {})
        for entry in conference.get("entryPoints", []):
            if entry.get("entryPointType") == "video":
                uri = entry.get("uri", "")
                if "meet.google.com" in uri or "teams.microsoft.com" in uri or "zoom.us" in uri:
                    return uri
        
        # Check hangoutLink (older Meet format)
        hangout = event.get("hangoutLink")
        if hangout:
            return hangout
        
        # Check description/location for meeting URLs
        description = event.get("description", "") + " " + event.get("location", "")
        for domain in ["meet.google.com", "teams.microsoft.com", "zoom.us"]:
            if domain in description:
                # Extract URL
                for word in description.split():
                    if domain in word and word.startswith("http"):
                        return word
        
        return None
    
    def _detect_platform(self, url: str) -> str:
        """Detect meeting platform from URL."""
        if "meet.google.com" in url:
            return "google_meet"
        elif "teams.microsoft.com" in url:
            return "teams"
        elif "zoom.us" in url:
            return "zoom"
        return "google_meet"
    
    async def auto_join_upcoming(self, db: Session) -> int:
        """
        Check for upcoming meetings and automatically send bots.
        
        Returns number of bots sent.
        """
        upcoming = await self.get_upcoming_meetings(db)
        
        if not upcoming:
            return 0
        
        sent = 0
        for event in upcoming:
            # Check if we already have a meeting for this calendar event
            existing = db.query(Meeting).filter(
                Meeting.meeting_url == event["meet_url"]
            ).first()
            
            if existing:
                continue  # Already tracking this meeting
            
            # Create meeting + send bot
            try:
                platform = self._detect_platform(event["meet_url"])
                
                meeting = Meeting(
                    title=event["summary"],
                    meeting_url=event["meet_url"],
                    platform=platform,
                    status="scheduled",
                    scheduled_at=event["start"] or datetime.now(timezone.utc).isoformat(),
                    participants=[],
                )
                db.add(meeting)
                db.commit()
                db.refresh(meeting)
                
                # Send bot
                bot_data = await recall_service.create_bot(
                    meeting_url=event["meet_url"],
                    meeting_id=meeting.id,
                    bot_name=f"MeetMind Bot - {event['summary'][:30]}",
                )
                
                meeting.recall_bot_id = bot_data["id"]
                meeting.status = "bot_created"
                db.commit()
                
                sent += 1
                logger.info(f"Auto-joined meeting: {event['summary']} ({event['meet_url'][:40]}...)")
                
            except RecallServiceError as e:
                logger.error(f"Failed to send bot for {event['summary']}: {e}")
            except Exception as e:
                logger.error(f"Error auto-joining {event['summary']}: {e}")
                db.rollback()
        
        return sent


# Global service instance
calendar_service = CalendarService()
