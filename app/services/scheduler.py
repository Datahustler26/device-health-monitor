"""Background scheduler for analysis tasks."""

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
import logging
from app.config import settings
from app.db.session import SessionLocal
from app.services.battery_analyzer import BatteryAnalyzer
from app.services.rca_engine import RCAEngine

logger = logging.getLogger(__name__)

scheduler = None


def battery_analysis_job():
    """Background job for battery analysis."""
    
    try:
        db = SessionLocal()
        BatteryAnalyzer.analyze_all_devices(db)
        db.close()
    except Exception as e:
        logger.error(f"Error in battery analysis job: {e}")


def rca_generation_job():
    """Background job for RCA generation."""
    
    try:
        db = SessionLocal()
        RCAEngine.run_rca_for_active_alerts(db)
        db.close()
    except Exception as e:
        logger.error(f"Error in RCA generation job: {e}")


def start_scheduler():
    """Start the background scheduler."""
    
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # Add battery analysis job
        scheduler.add_job(
            battery_analysis_job,
            'interval',
            seconds=settings.analyzer_interval_seconds,
            id='battery_analysis',
            name='Battery Health Analysis',
            replace_existing=True
        )
        
        # Add RCA generation job
        scheduler.add_job(
            rca_generation_job,
            'interval',
            seconds=settings.rca_interval_seconds,
            id='rca_generation',
            name='RCA Report Generation',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info(f"Scheduler started with {len(scheduler.get_jobs())} jobs")
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise


def stop_scheduler():
    """Stop the background scheduler."""
    
    global scheduler
    
    if scheduler is None:
        logger.warning("Scheduler not running")
        return
    
    try:
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Scheduler stopped")
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
