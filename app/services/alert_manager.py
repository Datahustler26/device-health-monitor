"""Alert management service."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
import requests
import json
from app.config import settings
from app.models.device import Alert, AlertSeverity, AlertStatus, Device
from app.services.slack_notifier import send_slack_alert

logger = logging.getLogger(__name__)


class AlertManager:
    """Manage alert creation, dispatch, and resolution."""
    
    @staticmethod
    def create_alert(
        db: Session,
        device_id: str,
        alert_type: str,
        severity: AlertSeverity,
        message: str,
        triggered_value: Optional[float] = None,
        threshold_value: Optional[float] = None
    ) -> Alert:
        """Create a new alert."""
        
        try:
            # Check if similar alert already exists
            existing_alert = db.query(Alert).filter(
                and_(
                    Alert.device_id == device_id,
                    Alert.alert_type == alert_type,
                    Alert.status == AlertStatus.ACTIVE
                )
            ).first()
            
            if existing_alert:
                logger.info(f"Alert already exists for {device_id} - {alert_type}")
                return existing_alert
            
            # Create new alert
            alert = Alert(
                device_id=device_id,
                alert_type=alert_type,
                severity=severity,
                status=AlertStatus.ACTIVE,
                message=message,
                triggered_value=triggered_value,
                threshold_value=threshold_value
            )
            
            db.add(alert)
            db.commit()
            
            logger.info(f"Alert created: {device_id} - {alert_type} (severity={severity})")
            
            # Send notifications
            AlertManager.dispatch_alert(db, alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def dispatch_alert(db: Session, alert: Alert):
        """Dispatch alert via configured channels."""
        
        try:
            device = db.query(Device).filter(Device.device_id == alert.device_id).first()
            
            # Slack notification
            if settings.slack_enabled and settings.slack_webhook_url:
                AlertManager._send_slack_notification(alert, device)
            
            # Email notification
            if settings.email_alerts_enabled and alert.severity == AlertSeverity.CRITICAL:
                AlertManager._send_email_notification(alert, device)
            
        except Exception as e:
            logger.error(f"Error dispatching alert {alert.id}: {e}")
    
    @staticmethod
    def _send_slack_notification(alert: Alert, device: Optional[Device]):
        """Send Slack notification."""
        
        try:
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ffa500",
                AlertSeverity.CRITICAL: "#ff0000"
            }
            
            device_name = device.device_name if device else alert.device_id
            device_type = device.device_type if device else "Unknown"
            
            message = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#808080"),
                        "title": f"🚨 Alert: {alert.alert_type}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Device ID", "value": alert.device_id, "short": True},
                            {"title": "Device Name", "value": device_name, "short": True},
                            {"title": "Type", "value": device_type, "short": True},
                            {"title": "Severity", "value": alert.severity.value, "short": True},
                            {"title": "Triggered Value", "value": str(alert.triggered_value or "N/A"), "short": True},
                            {"title": "Threshold", "value": str(alert.threshold_value or "N/A"), "short": True},
                        ],
                        "footer": "Device Health Monitoring System",
                        "ts": int(alert.created_at.timestamp())
                    }
                ]
            }
            
            response = requests.post(
                settings.slack_webhook_url,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent for alert {alert.id}")
            else:
                logger.warning(f"Slack notification failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    @staticmethod
    def _send_email_notification(alert: Alert, device: Optional[Device]):
        """Send email notification (stub for demonstration)."""
        
        try:
            # This is a stub - implement SMTP sending as needed
            logger.info(f"Email notification would be sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Acknowledge an alert."""
        
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return None
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Alert {alert_id} acknowledged")
            return alert
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def resolve_alert(
        db: Session,
        alert_id: int,
        resolution_notes: str
    ) -> Optional[Alert]:
        """Resolve an alert."""
        
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return None
            
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = resolution_notes
            db.commit()
            
            logger.info(f"Alert {alert_id} resolved: {resolution_notes}")
            return alert
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_active_alerts(db: Session, limit: int = 100) -> List[Alert]:
        """Get all active alerts."""
        
        try:
            return db.query(Alert).filter(
                Alert.status == AlertStatus.ACTIVE
            ).order_by(Alert.created_at.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error fetching active alerts: {e}")
            return []
