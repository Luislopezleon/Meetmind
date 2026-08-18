"""
NotionService - Publishes meeting summaries and insights as Notion pages.

Uses the Notion API with an integration token.
When a meeting completes and the AI generates a summary, it can be
automatically published as a rich Notion page.
"""

import httpx
from typing import Optional, Dict, Any, List
from loguru import logger
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Meeting, MeetingSummary, ActionItem, Decision, Risk, OpenQuestion
from app.models.integrations import IntegrationConfig


class NotionServiceError(Exception):
    """Exception for Notion service errors."""
    pass


class NotionService:
    """Service to interact with Notion API."""
    
    NOTION_API = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    def _get_config(self, db: Session) -> Optional[Dict[str, Any]]:
        """Get Notion config from database."""
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.integration_type == "notion",
            IntegrationConfig.enabled == True
        ).first()
        
        if not config:
            return None
        return config.config
    
    def _headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }
    
    async def is_connected(self, db: Session) -> bool:
        """Check if Notion is configured and accessible."""
        config = self._get_config(db)
        if not config:
            return False
        
        try:
            api_key = config.get("api_key", "")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.NOTION_API}/users/me",
                    headers=self._headers(api_key),
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def publish_meeting_summary(
        self,
        meeting: Meeting,
        db: Session,
    ) -> Optional[str]:
        """
        Publish a meeting's summary + insights as a Notion page.
        
        Returns the Notion page URL or None if not configured.
        """
        config = self._get_config(db)
        if not config:
            logger.debug("Notion not configured, skipping publish")
            return None
        
        api_key = config.get("api_key", "")
        parent_page_id = config.get("parent_page_id", "")
        
        if not api_key or not parent_page_id:
            logger.warning("Notion api_key or parent_page_id not configured")
            return None
        
        # Gather meeting data
        summary = db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting.id).first()
        action_items = db.query(ActionItem).filter(ActionItem.meeting_id == meeting.id).all()
        decisions = db.query(Decision).filter(Decision.meeting_id == meeting.id).all()
        risks = db.query(Risk).filter(Risk.meeting_id == meeting.id).all()
        questions = db.query(OpenQuestion).filter(OpenQuestion.meeting_id == meeting.id).all()
        
        if not summary:
            logger.info(f"No summary for meeting {meeting.id}, skipping Notion publish")
            return None
        
        # Build Notion page content
        children = self._build_page_content(meeting, summary, action_items, decisions, risks, questions)
        
        payload = {
            "parent": {"page_id": parent_page_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": f"Meeting: {meeting.title}"}}]
                }
            },
            "children": children,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.NOTION_API}/pages",
                    headers=self._headers(api_key),
                    json=payload,
                    timeout=15.0,
                )
                
                if response.status_code == 200:
                    page_data = response.json()
                    page_url = page_data.get("url", "")
                    page_id = page_data.get("id", "")
                    
                    # Update summary with Notion reference
                    summary.notion_page_id = page_id
                    db.commit()
                    
                    logger.info(f"Published meeting {meeting.id} summary to Notion: {page_url}")
                    return page_url
                else:
                    error = response.text[:200]
                    logger.error(f"Failed to publish to Notion: {response.status_code} - {error}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Notion request error: {e}")
            return None
    
    def _build_page_content(
        self,
        meeting: Meeting,
        summary: MeetingSummary,
        action_items: List[ActionItem],
        decisions: List[Decision],
        risks: List[Risk],
        questions: List[OpenQuestion],
    ) -> List[Dict]:
        """Build Notion block children for the page."""
        blocks: List[Dict] = []
        
        # Meeting metadata
        blocks.append(self._callout_block(
            f"📅 {meeting.platform.replace('_', ' ').title()} · "
            f"{'%s' % ', '.join(meeting.participants) if meeting.participants else 'No participants recorded'}"
        ))
        blocks.append(self._divider())
        
        # Summary
        blocks.append(self._heading("Summary", level=2))
        # Split summary into paragraphs
        clean_summary = (summary.executive_summary or "")
        clean_summary = clean_summary.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
        for paragraph in clean_summary.split("\n"):
            p = paragraph.strip()
            if p:
                blocks.append(self._paragraph(p))
        
        # Action Items
        if action_items:
            blocks.append(self._divider())
            blocks.append(self._heading("Action Items", level=2))
            for item in action_items:
                text = item.task
                if item.assignee:
                    text += f" → @{item.assignee}"
                if item.deadline:
                    text += f" (due: {item.deadline})"
                blocks.append(self._todo_block(text))
        
        # Decisions
        if decisions:
            blocks.append(self._divider())
            blocks.append(self._heading("Decisions", level=2))
            for d in decisions:
                blocks.append(self._bullet(d.decision))
        
        # Risks
        if risks:
            blocks.append(self._divider())
            blocks.append(self._heading("Risks", level=2))
            for r in risks:
                blocks.append(self._bullet(f"⚠️ {r.risk_description} [{r.severity}]"))
        
        # Open Questions
        if questions:
            blocks.append(self._divider())
            blocks.append(self._heading("Open Questions", level=2))
            for q in questions:
                blocks.append(self._bullet(f"❓ {q.question}"))
        
        return blocks[:100]  # Notion limit per request
    
    def _heading(self, text: str, level: int = 2) -> Dict:
        key = f"heading_{level}"
        return {
            "object": "block",
            "type": key,
            key: {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }
    
    def _paragraph(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
        }
    
    def _bullet(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
        }
    
    def _todo_block(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": text[:2000]}}],
                "checked": False,
            },
        }
    
    def _callout_block(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": text[:2000]}}],
                "icon": {"emoji": "🧠"},
            },
        }
    
    def _divider(self) -> Dict:
        return {"object": "block", "type": "divider", "divider": {}}


# Global service instance
notion_service = NotionService()
