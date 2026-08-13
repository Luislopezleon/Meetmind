from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict

from app.db.database import get_db
from app.db.redis import redis_manager
from app.schemas import HealthCheck
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)) -> HealthCheck:
    """
    Health check endpoint that verifies all services are running properly.
    
    Returns status of:
    - API service (FastAPI)
    - Database (PostgreSQL)
    - Cache (Redis)
    """
    services: Dict[str, str] = {}
    
    # Check FastAPI
    services["api"] = "healthy"
    
    # Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"unhealthy: {str(e)[:50]}"
    
    # Check Redis
    try:
        if redis_manager.redis_client:
            await redis_manager.redis_client.ping()
            services["redis"] = "healthy"
        else:
            services["redis"] = "unhealthy: not connected"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)[:50]}"
    
    # Determine overall status
    overall_status = "healthy" if all(
        status == "healthy" for status in services.values()
    ) else "unhealthy"
    
    return HealthCheck(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.version,
        services=services
    )