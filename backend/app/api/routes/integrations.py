"""API routes for managing integration configurations (Jira, Notion, Calendar)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.models.integrations import IntegrationConfig
from app.services.jira_service import jira_service
from app.services.notion_service import notion_service
from app.services.calendar_service import calendar_service

router = APIRouter()


# --- Schemas ---

class JiraConfig(BaseModel):
    url: str  # https://your-domain.atlassian.net
    email: str
    api_token: str
    project_key: str
    issue_type: str = "Task"


class NotionConfig(BaseModel):
    api_key: str
    parent_page_id: str


class GoogleCalendarConfig(BaseModel):
    access_token: str
    calendar_id: str = "primary"


class IntegrationStatus(BaseModel):
    integration_type: str
    enabled: bool
    status: str
    config_summary: Optional[dict] = None


# --- Endpoints ---

@router.get("/")
async def list_integrations(db: Session = Depends(get_db)):
    """List all integration configurations and their status."""
    integrations = db.query(IntegrationConfig).all()
    
    # Build a complete list (even for unconfigured ones)
    all_types = ["jira", "notion", "google_calendar"]
    configured = {i.integration_type: i for i in integrations}
    
    result = []
    for t in all_types:
        if t in configured:
            cfg = configured[t]
            # Don't expose secrets
            safe_config = {}
            if t == "jira" and cfg.config:
                safe_config = {
                    "url": cfg.config.get("url", ""),
                    "email": cfg.config.get("email", ""),
                    "project_key": cfg.config.get("project_key", ""),
                }
            elif t == "notion" and cfg.config:
                safe_config = {
                    "parent_page_id": cfg.config.get("parent_page_id", ""),
                }
            elif t == "google_calendar" and cfg.config:
                safe_config = {
                    "calendar_id": cfg.config.get("calendar_id", "primary"),
                }
            
            result.append({
                "integration_type": t,
                "enabled": cfg.enabled,
                "status": cfg.status,
                "config_summary": safe_config,
            })
        else:
            result.append({
                "integration_type": t,
                "enabled": False,
                "status": "disconnected",
                "config_summary": None,
            })
    
    return result


@router.post("/jira/connect")
async def connect_jira(config: JiraConfig, db: Session = Depends(get_db)):
    """Configure and test Jira connection."""
    # Test connection first
    test_config = config.model_dump()
    try:
        await jira_service._test_connection(test_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Jira connection failed: {e}")
    
    # Save config
    existing = db.query(IntegrationConfig).filter(
        IntegrationConfig.integration_type == "jira"
    ).first()
    
    if existing:
        existing.config = test_config
        existing.enabled = True
        existing.status = "connected"
        existing.error_message = None
    else:
        new_config = IntegrationConfig(
            integration_type="jira",
            enabled=True,
            status="connected",
            config=test_config,
        )
        db.add(new_config)
    
    db.commit()
    return {"status": "connected", "message": "Jira connected successfully"}


@router.post("/notion/connect")
async def connect_notion(config: NotionConfig, db: Session = Depends(get_db)):
    """Configure and test Notion connection."""
    # Test connection
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.notion.com/v1/users/me",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Notion-Version": "2022-06-28",
                },
                timeout=10.0,
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Notion connection failed: {response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Notion connection error: {e}")
    
    # Save config
    existing = db.query(IntegrationConfig).filter(
        IntegrationConfig.integration_type == "notion"
    ).first()
    
    config_data = config.model_dump()
    
    if existing:
        existing.config = config_data
        existing.enabled = True
        existing.status = "connected"
    else:
        new_config = IntegrationConfig(
            integration_type="notion",
            enabled=True,
            status="connected",
            config=config_data,
        )
        db.add(new_config)
    
    db.commit()
    return {"status": "connected", "message": "Notion connected successfully"}


@router.post("/google_calendar/connect")
async def connect_google_calendar(config: GoogleCalendarConfig, db: Session = Depends(get_db)):
    """Configure Google Calendar connection."""
    # Save config (token validation would need a real call)
    existing = db.query(IntegrationConfig).filter(
        IntegrationConfig.integration_type == "google_calendar"
    ).first()
    
    config_data = config.model_dump()
    
    if existing:
        existing.config = config_data
        existing.enabled = True
        existing.status = "connected"
    else:
        new_config = IntegrationConfig(
            integration_type="google_calendar",
            enabled=True,
            status="connected",
            config=config_data,
        )
        db.add(new_config)
    
    db.commit()
    return {"status": "connected", "message": "Google Calendar connected successfully"}


@router.post("/{integration_type}/disconnect")
async def disconnect_integration(integration_type: str, db: Session = Depends(get_db)):
    """Disconnect an integration."""
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.integration_type == integration_type
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    config.enabled = False
    config.status = "disconnected"
    db.commit()
    
    return {"status": "disconnected", "message": f"{integration_type} disconnected"}
