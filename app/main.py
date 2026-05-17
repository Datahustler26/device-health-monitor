"""Main FastAPI application entrypoint."""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import sys

from app.config import settings
from app.db.session import engine, Base, get_db
from app.models.schemas import HealthCheckResponse
from app.routers import devices, telemetry, alerts, health
from app.services.scheduler import start_scheduler, stop_scheduler
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready device health monitoring platform with automated alerts and RCA",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router, prefix="/api/v1", tags=["devices"])
app.include_router(telemetry.router, prefix="/api/v1", tags=["telemetry"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")
    
    if settings.scheduler_enabled:
        try:
            start_scheduler()
            logger.info("APScheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    logger.info(f"App startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    logger.info("Shutting down application")
    
    if settings.scheduler_enabled:
        try:
            stop_scheduler()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
