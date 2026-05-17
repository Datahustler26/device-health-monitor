"""Alert management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.device import Alert, AlertStatus
from app.models.schemas import AlertResponse, AlertResolve
from app.services.alert_manager import AlertManager
import logging

router = APIRouter(prefix="/alerts")
logger = logging.getLogger(__name__)


@router.get("/active", response_model=List[AlertResponse])
async def get_active_alerts(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all active alerts."""
    
    alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.ACTIVE
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    return alerts


@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts(
    status_filter: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all alerts with optional status filter."""
    
    query = db.query(Alert)
    
    if status_filter:
        try:
            status_enum = AlertStatus[status_filter.upper()]
            query = query.filter(Alert.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get alert by ID."""
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge an alert."""
    
    alert = AlertManager.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    return alert


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    resolution: AlertResolve,
    db: Session = Depends(get_db)
):
    """Resolve an alert with notes."""
    
    alert = AlertManager.resolve_alert(db, alert_id, resolution.resolution_notes)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    logger.info(f"Alert {alert_id} resolved")
    return alert


@router.get("/device/{device_id}", response_model=List[AlertResponse])
async def get_device_alerts(
    device_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get alerts for a specific device."""
    
    alerts = db.query(Alert).filter(
        Alert.device_id == device_id
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    return alerts
