"""Models for storing integration configurations."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class IntegrationConfig(Base):
    """
    Stores integration configurations.
    
    In the future with multi-tenancy, this would have a user_id FK.
    For POC, it's a singleton per integration type.
    """
    __tablename__ = "integration_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Integration type: jira, notion, google_calendar
    integration_type = Column(String(50), unique=True, nullable=False, index=True)
    
    # Is it enabled/connected?
    enabled = Column(Boolean, default=False)
    
    # Connection details (varies by integration)
    # Jira: {url, email, api_token, project_key, issue_type}
    # Notion: {api_key, database_id}
    # Google Calendar: {credentials_json, calendar_id}
    config = Column(JSON, default=dict)
    
    # Status
    status = Column(String(50), default="disconnected")  # disconnected, connected, error
    last_sync_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
