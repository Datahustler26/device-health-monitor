"""Telemetry ingestion and querying routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.device import Telemetry, Device
from app.models.schemas import TelemetryIngest, TelemetryResponse
from app.utils.validators import Validators
import logging

router = APIRouter(prefix="/telemetry")
logger = logging.getLogger(__name__)


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry(
    telemetry_data: TelemetryIngest,
    db: Session = Depends(get_db)
):
    """Ingest device telemetry event."""
    
    # Validate device exists
    device = db.query(Device).filter(Device.device_id == telemetry_data.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {telemetry_data.device_id} not found. Please register device first."
        )
    
    # Validate inputs
    if not Validators.validate_battery_percentage(telemetry_data.battery_pct):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Battery percentage must be 0-100"
        )
    
    if not Validators.validate_temperature(telemetry_data.temperature_celsius):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Temperature must be between -50 and 100°C"
        )
    
    if not Validators.validate_event_id(telemetry_data.event_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid event ID"
        )
    
    # Check for duplicate event
    existing = db.query(Telemetry).filter(Telemetry.event_id == telemetry_data.event_id).first()
    if existing:
        logger.info(f"Duplicate event skipped: {telemetry_data.event_id}")
        return {"status": "duplicate", "event_id": telemetry_data.event_id}
    
    # Set timestamp if not provided
    event_timestamp = telemetry_data.event_timestamp or datetime.utcnow()
    
    # Create telemetry record
    telemetry = Telemetry(
        device_id=telemetry_data.device_id,
        battery_pct=telemetry_data.battery_pct,
        temperature_celsius=telemetry_data.temperature_celsius,
        humidity_pct=telemetry_data.humidity_pct,
        connectivity_status=telemetry_data.connectivity_status,
        signal_strength=telemetry_data.signal_strength,
        charge_cycles=telemetry_data.charge_cycles,
        firmware_version=telemetry_data.firmware_version,
        uptime_seconds=telemetry_data.uptime_seconds,
        memory_used_mb=telemetry_data.memory_used_mb,
        cpu_usage_pct=telemetry_data.cpu_usage_pct,
        event_timestamp=event_timestamp,
        event_id=telemetry_data.event_id
    )
    
    db.add(telemetry)
    
    # Update device last_seen
    device.last_seen = datetime.utcnow()
    device.firmware_version = telemetry_data.firmware_version
    
    db.commit()
    
    logger.info(
        f"Telemetry ingested: {telemetry_data.device_id} "
        f"battery={telemetry_data.battery_pct}% "
        f"temp={telemetry_data.temperature_celsius}°C"
    )
    
    return {"status": "ingested", "event_id": telemetry_data.event_id}


@router.get("/{device_id}", response_model=List[TelemetryResponse])
async def get_telemetry(
    device_id: str,
    hours: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get telemetry records for a device."""
    
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    since = datetime.utcnow() - timedelta(hours=hours)
    
    telemetry_records = db.query(Telemetry).filter(
        Telemetry.device_id == device_id,
        Telemetry.event_timestamp >= since
    ).order_by(desc(Telemetry.event_timestamp)).limit(limit).all()
    
    return telemetry_records


@router.get("/{device_id}/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Get latest telemetry for a device."""
    
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    telemetry = db.query(Telemetry).filter(
        Telemetry.device_id == device_id
    ).order_by(desc(Telemetry.event_timestamp)).first()
    
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for device {device_id}"
        )
    
    return telemetry
