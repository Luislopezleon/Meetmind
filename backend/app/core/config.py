from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "MeetMind"
    version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "postgresql://meetmind:meetmind@localhost:5432/meetmind"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Keys
    gemini_api_key: Optional[str] = None
    recall_ai_api_key: Optional[str] = None
    
    # Recall.ai Configuration
    recall_region: str = "eu-central-1"
    
    # Jira Configuration
    jira_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    
    # Notion Configuration
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None
    
    # URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    
    # Webhook Configuration
    recall_webhook_secret: Optional[str] = None
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()