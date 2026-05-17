"""Health check and status routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.db.session import get_db
from app.config import settings
from app.models.schemas import HealthCheckResponse, FleetSummaryResponse, BatteryHealthResponse
from app.models.device import Device, Alert, AlertStatus, Telemetry, BatteryHistory
from app.services.battery_analyzer import BatteryAnalyzer
from app.services.rca_engine import RCAEngine
from app.services.scheduler import scheduler
import logging

router = APIRouter(prefix="/health")
logger = logging.getLogger(__name__)


@router.get("", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    
    # Check database connectivity
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check scheduler status
    scheduler_status = "running" if scheduler and scheduler.running else "stopped"
    
    return HealthCheckResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        timestamp=datetime.utcnow(),
        database_status=db_status,
        scheduler_status=scheduler_status,
        version=settings.app_version
    )


@router.get("/fleet/summary", response_model=FleetSummaryResponse)
async def get_fleet_summary(db: Session = Depends(get_db)):
    """Get fleet-wide health summary."""
    
    try:
        # Count devices
        total_devices = db.query(Device).count()
        active_devices = db.query(Device).filter(Device.status == "ACTIVE").count()
        inactive_devices = total_devices - active_devices
        
        # Battery health distribution
        latest_battery_records = db.query(BatteryHistory).from_statement(
            text("""
                SELECT DISTINCT ON (device_id) * FROM battery_history 
                ORDER BY device_id, timestamp DESC
            """)
        ).all()
        
        healthy = sum(1 for b in latest_battery_records if b.state.value == "HEALTHY")
        warning = sum(1 for b in latest_battery_records if b.state.value == "WARNING")
        critical = sum(1 for b in latest_battery_records if b.state.value == "CRITICAL")
        
        # Alert statistics
        active_alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).count()
        devices_with_critical = db.query(Alert).filter(
            Alert.status == AlertStatus.ACTIVE,
            Alert.severity.in_(["CRITICAL"])
        ).distinct(Alert.device_id).count()
        
        # Calculate averages
        latest_telemetry = db.query(Telemetry).from_statement(
            text("""
                SELECT DISTINCT ON (device_id) * FROM telemetry 
                ORDER BY device_id, event_timestamp DESC
            """)
        ).all()
        
        avg_battery = sum(t.battery_pct for t in latest_telemetry) / len(latest_telemetry) if latest_telemetry else 0
        avg_temp = sum(t.temperature_celsius for t in latest_telemetry) / len(latest_telemetry) if latest_telemetry else 0
        connected = sum(1 for t in latest_telemetry if t.connectivity_status == "CONNECTED")
        connectivity_rate = (connected / len(latest_telemetry) * 100) if latest_telemetry else 0
        
        return FleetSummaryResponse(
            total_devices=total_devices,
            active_devices=active_devices,
            inactive_devices=inactive_devices,
            healthy_batteries=healthy,
            warning_batteries=warning,
            critical_batteries=critical,
            active_alerts_count=active_alerts,
            devices_with_critical_alerts=devices_with_critical,
            avg_battery_pct=round(avg_battery, 2),
            avg_temperature=round(avg_temp, 2),
            connectivity_rate=round(connectivity_rate, 2)
        )
        
    except Exception as e:
        logger.error(f"Error generating fleet summary: {e}")
        # Return minimal valid response on error
        return FleetSummaryResponse(
            total_devices=0,
            active_devices=0,
            inactive_devices=0,
            healthy_batteries=0,
            warning_batteries=0,
            critical_batteries=0,
            active_alerts_count=0,
            devices_with_critical_alerts=0,
            avg_battery_pct=0,
            avg_temperature=0,
            connectivity_rate=0
        )


@router.get("/devices/{device_id}/battery", response_model=BatteryHealthResponse)
async def get_device_battery_health(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Get battery health analysis for a device."""
    
    # Perform analysis
    battery_analysis = BatteryAnalyzer.analyze_device_battery(db, device_id)
    
    if not battery_analysis:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Device not found or no telemetry available")
    
    return battery_analysis


@router.get("/devices/{device_id}/rca")
async def get_device_rca(device_id: str, db: Session = Depends(get_db)):
    """Get latest RCA report for a device."""
    
    rca_report = db.query(RCAEngine).filter(
        RCAEngine.device_id == device_id
    ).order_by(RCAEngine.generated_at.desc()).first()
    
    if not rca_report:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No RCA reports found for device")
    
    return {
        "id": rca_report.id,
        "device_id": rca_report.device_id,
        "alert_type": rca_report.alert_type,
        "probable_cause": rca_report.probable_cause,
        "recommended_action": rca_report.recommended_action,
        "confidence": rca_report.confidence_score,
        "generated_at": rca_report.generated_at
    }
