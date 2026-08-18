"""
JiraService - Creates Jira issues from detected action items.

Uses Jira REST API with API token authentication.
Each action item detected by the agent can be automatically synced
as a Jira issue in the configured project.
"""

import httpx
from typing import Optional, Dict, Any
from loguru import logger
from sqlalchemy.orm import Session
from base64 import b64encode

from app.models import ActionItem
from app.models.integrations import IntegrationConfig


class JiraServiceError(Exception):
    """Exception for Jira service errors."""
    pass


class JiraService:
    """Service to interact with Jira REST API."""
    
    def _get_config(self, db: Session) -> Optional[Dict[str, Any]]:
        """Get Jira config from database."""
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.integration_type == "jira",
            IntegrationConfig.enabled == True
        ).first()
        
        if not config:
            return None
        return config.config
    
    def _get_auth_header(self, email: str, api_token: str) -> str:
        """Create Basic auth header for Jira API."""
        credentials = b64encode(f"{email}:{api_token}".encode()).decode()
        return f"Basic {credentials}"
    
    async def is_connected(self, db: Session) -> bool:
        """Check if Jira is configured and accessible."""
        config = self._get_config(db)
        if not config:
            return False
        
        try:
            await self._test_connection(config)
            return True
        except Exception:
            return False
    
    async def _test_connection(self, config: Dict[str, Any]) -> bool:
        """Test Jira API connection."""
        url = config.get("url", "").rstrip("/")
        email = config.get("email", "")
        api_token = config.get("api_token", "")
        
        if not all([url, email, api_token]):
            raise JiraServiceError("Incomplete Jira configuration")
        
        auth = self._get_auth_header(email, api_token)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}/rest/api/3/myself",
                headers={"Authorization": auth, "Accept": "application/json"},
                timeout=10.0,
            )
            
            if response.status_code == 200:
                return True
            else:
                raise JiraServiceError(f"Jira connection failed: {response.status_code}")
    
    async def create_issue_from_action_item(
        self,
        action_item: ActionItem,
        db: Session,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Jira issue from a detected action item.
        
        Returns the created issue data (key, id, url) or None if Jira is not configured.
        """
        config = self._get_config(db)
        if not config:
            logger.debug("Jira not configured, skipping issue creation")
            return None
        
        url = config["url"].rstrip("/")
        email = config["email"]
        api_token = config["api_token"]
        project_key = config.get("project_key", "")
        issue_type = config.get("issue_type", "Task")
        
        if not project_key:
            logger.warning("Jira project_key not configured")
            return None
        
        auth = self._get_auth_header(email, api_token)
        
        # Build issue payload
        priority_map = {"high": "High", "medium": "Medium", "low": "Low"}
        
        description = f"Detected by MeetMind AI from meeting transcript.\n\n"
        if action_item.deadline:
            description += f"*Deadline:* {action_item.deadline}\n"
        if action_item.assignee:
            description += f"*Assignee mentioned:* {action_item.assignee}\n"
        description += f"\n_Confidence: {action_item.confidence_score or 'N/A'}_"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": action_item.task[:255],  # Jira limit
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority_map.get(action_item.priority or "medium", "Medium")},
                "labels": ["meetmind", "ai-detected"],
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{url}/rest/api/3/issue",
                    headers={
                        "Authorization": auth,
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=15.0,
                )
                
                if response.status_code == 201:
                    issue_data = response.json()
                    issue_key = issue_data["key"]
                    issue_id = issue_data["id"]
                    
                    # Update action item with Jira reference
                    action_item.jira_issue_key = issue_key
                    action_item.jira_issue_id = issue_id
                    db.commit()
                    
                    logger.info(f"Created Jira issue {issue_key} from action item '{action_item.task[:50]}'")
                    
                    return {
                        "key": issue_key,
                        "id": issue_id,
                        "url": f"{url}/browse/{issue_key}",
                    }
                else:
                    error = response.text[:200]
                    logger.error(f"Failed to create Jira issue: {response.status_code} - {error}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Jira request error: {e}")
            return None
    
    async def sync_meeting_action_items(
        self,
        meeting_id: int,
        db: Session,
    ) -> int:
        """
        Sync all action items from a meeting to Jira.
        
        Returns the number of issues created.
        """
        config = self._get_config(db)
        if not config:
            return 0
        
        # Get action items without Jira issue
        action_items = db.query(ActionItem).filter(
            ActionItem.meeting_id == meeting_id,
            ActionItem.jira_issue_key == None,
        ).all()
        
        if not action_items:
            return 0
        
        created = 0
        for item in action_items:
            result = await self.create_issue_from_action_item(item, db)
            if result:
                created += 1
        
        logger.info(f"Synced {created}/{len(action_items)} action items to Jira for meeting {meeting_id}")
        return created


# Global service instance
jira_service = JiraService()
