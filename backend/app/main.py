from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.db.database import engine
from app.db.redis import redis_manager
from app.models import Base
from app.api.routes import health, meetings, webhooks, websockets
from app.schemas import ErrorResponse


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up MeetMind application...")
    
    # Note: Database schema is managed by Alembic migrations.
    # Run 'alembic upgrade head' to apply migrations.
    logger.info("Database schema managed by Alembic migrations")
    
    # Connect to Redis
    try:
        await redis_manager.connect()
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    logger.info("MeetMind application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MeetMind application...")
    
    # Disconnect from Redis
    try:
        await redis_manager.disconnect()
        logger.info("Disconnected from Redis")
    except Exception as e:
        logger.error(f"Error disconnecting from Redis: {e}")
    
    logger.info("MeetMind application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Real-Time Meeting Intelligence Agent - Autonomous AI agent for meetings",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred"
        ).model_dump()
    )


# Health check middleware
@app.middleware("http")
async def health_check_middleware(request: Request, call_next):
    """Middleware to add request ID and basic logging."""
    logger.info(f"{request.method} {request.url}")
    
    response = await call_next(request)
    
    logger.info(f"Response status: {response.status_code}")
    return response


# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(meetings.router, prefix="/api/v1/meetings", tags=["meetings"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic application info."""
    return {
        "app": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "status": "healthy"
    }