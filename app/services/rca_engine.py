"""Root Cause Analysis (RCA) engine service."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import json
import logging
from app.config import settings
from app.models.device import Telemetry, Alert, RCAReport, Device, BatteryHistory, AlertStatus

logger = logging.getLogger(__name__)


class RCAEngine:
    """Root Cause Analysis engine for alerts."""
    
    @staticmethod
    def analyze_alert(db: Session, alert: Alert) -> Optional[RCAReport]:
        """Generate RCA report for an alert."""
        
        try:
            device = db.query(Device).filter(Device.device_id == alert.device_id).first()
            if not device:
                logger.warning(f"Device not found: {alert.device_id}")
                return None
            
            # Get analysis based on alert type
            if alert.alert_type == "BATTERY_CRITICAL":
                analysis_data = RCAEngine._analyze_battery_critical(db, alert, device)
            elif alert.alert_type == "TEMP_BREACH":
                analysis_data = RCAEngine._analyze_temp_breach(db, alert, device)
            elif alert.alert_type == "CONNECTIVITY_LOSS":
                analysis_data = RCAEngine._analyze_connectivity_loss(db, alert, device)
            elif alert.alert_type == "FIRMWARE_EOL":
                analysis_data = RCAEngine._analyze_firmware_eol(db, alert, device)
            else:
                analysis_data = {"type": "unknown", "issues": []}
            
            # Create RCA report
            rca_report = RCAReport(
                device_id=alert.device_id,
                alert_id=alert.id,
                alert_type=alert.alert_type,
                probable_cause=analysis_data.get("probable_cause", "Unknown cause"),
                recommended_action=analysis_data.get("recommended_action", "Review alert details"),
                confidence_score=analysis_data.get("confidence", 0.5),
                analysis_data=json.dumps(analysis_data)
            )
            
            db.add(rca_report)
            db.commit()
            
            logger.info(
                f"RCA generated for {alert.device_id} - {alert.alert_type}: "
                f"confidence={rca_report.confidence_score:.2f}"
            )
            
            return rca_report
            
        except Exception as e:
            logger.error(f"Error generating RCA for alert {alert.id}: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def _analyze_battery_critical(
        db: Session,
        alert: Alert,
        device: Device
    ) -> Dict[str, Any]:
        """Analyze critical battery alert."""
        
        # Get recent telemetry
        since = datetime.utcnow() - timedelta(hours=24)
        telemetry_records = db.query(Telemetry).filter(
            and_(
                Telemetry.device_id == device.device_id,
                Telemetry.event_timestamp >= since
            )
        ).order_by(Telemetry.event_timestamp).all()
        
        issues = []
        confidence = 0.0
        
        if not telemetry_records:
            return {
                "type": "battery_critical",
                "issues": ["No telemetry data available for analysis"],
                "probable_cause": "Device appears offline; battery status unknown",
                "recommended_action": "Check device connectivity and power status",
                "confidence": 0.3
            }
        
        latest = telemetry_records[-1]
        
        # Check for accelerated discharge
        if len(telemetry_records) > 1:
            first = telemetry_records[0]
            discharge_rate = (first.battery_pct - latest.battery_pct) / 24
            if discharge_rate > 5:
                issues.append(f"Accelerated discharge: {discharge_rate:.1f}%/hour")
                confidence = 0.9
        
        # Check battery health history
        battery_history = db.query(BatteryHistory).filter(
            BatteryHistory.device_id == device.device_id
        ).order_by(desc(BatteryHistory.timestamp)).first()
        
        if battery_history:
            if battery_history.charge_cycles > 500 and battery_history.degradation_pct > 20:
                issues.append(f"Battery at end-of-life: {battery_history.charge_cycles} cycles, "
                             f"{battery_history.degradation_pct:.1f}% degradation")
                confidence = 0.95
            elif battery_history.degradation_pct > 10:
                issues.append(f"Battery degradation detected: {battery_history.degradation_pct:.1f}%")
                confidence = 0.85
        
        # Temperature influence
        if latest.temperature_celsius > settings.temp_max_threshold:
            issues.append(f"High temperature: {latest.temperature_celsius}°C may accelerate discharge")
            confidence = max(confidence, 0.8)
        
        probable_cause = "; ".join(issues) if issues else "Battery capacity reduced"
        recommended_action = "Schedule battery replacement within 24 hours"
        
        if battery_history and battery_history.charge_cycles > 500:
            recommended_action = "Battery replacement required - end-of-life threshold exceeded"
        
        return {
            "type": "battery_critical",
            "issues": issues,
            "battery_pct": latest.battery_pct,
            "temperature": latest.temperature_celsius,
            "charge_cycles": latest.charge_cycles,
            "probable_cause": probable_cause,
            "recommended_action": recommended_action,
            "confidence": min(confidence, 1.0)
        }
    
    @staticmethod
    def _analyze_temp_breach(
        db: Session,
        alert: Alert,
        device: Device
    ) -> Dict[str, Any]:
        """Analyze temperature breach alert."""
        
        since = datetime.utcnow() - timedelta(hours=6)
        telemetry_records = db.query(Telemetry).filter(
            and_(
                Telemetry.device_id == device.device_id,
                Telemetry.event_timestamp >= since
            )
        ).order_by(Telemetry.event_timestamp).all()
        
        if not telemetry_records:
            return {
                "type": "temp_breach",
                "probable_cause": "Unable to retrieve temperature data",
                "recommended_action": "Check device connectivity",
                "confidence": 0.3
            }
        
        # Analyze trend
        temps = [t.temperature_celsius for t in telemetry_records]
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        
        issues = [f"Temperature exceeded threshold: max={max_temp}°C, avg={avg_temp:.1f}°C"]
        confidence = 0.85
        
        # Check for sustained high temperature
        recent_high = sum(1 for t in temps[-10:] if t > settings.temp_max_threshold)
        if recent_high > 7:
            issues.append("Sustained high temperature - device may be in warm environment")
            confidence = 0.9
        
        probable_cause = "; ".join(issues)
        recommended_action = "Move device to cooler location or improve ventilation"
        
        return {
            "type": "temp_breach",
            "issues": issues,
            "max_temperature": max_temp,
            "avg_temperature": avg_temp,
            "probable_cause": probable_cause,
            "recommended_action": recommended_action,
            "confidence": confidence
        }
    
    @staticmethod
    def _analyze_connectivity_loss(
        db: Session,
        alert: Alert,
        device: Device
    ) -> Dict[str, Any]:
        """Analyze connectivity loss alert."""
        
        return {
            "type": "connectivity_loss",
            "probable_cause": f"Device {device.device_id} has not reported telemetry within SLA window",
            "recommended_action": "Check device network connectivity and power status; restart if necessary",
            "confidence": 0.7
        }
    
    @staticmethod
    def _analyze_firmware_eol(
        db: Session,
        alert: Alert,
        device: Device
    ) -> Dict[str, Any]:
        """Analyze firmware end-of-life alert."""
        
        return {
            "type": "firmware_eol",
            "probable_cause": f"Firmware version {device.firmware_version} is end-of-life",
            "recommended_action": "Schedule firmware update to latest stable version",
            "confidence": 0.95
        }
    
    @staticmethod
    def run_rca_for_active_alerts(db: Session) -> int:
        """Generate RCA for all active critical alerts."""
        
        try:
            active_critical_alerts = db.query(Alert).filter(
                and_(
                    Alert.status == AlertStatus.ACTIVE,
                    Alert.severity.in_(["CRITICAL", "WARNING"])
                )
            ).all()
            
            rca_count = 0
            for alert in active_critical_alerts:
                # Check if RCA already exists
                existing_rca = db.query(RCAReport).filter(
                    RCAReport.alert_id == alert.id
                ).first()
                
                if not existing_rca:
                    rca = RCAEngine.analyze_alert(db, alert)
                    if rca:
                        rca_count += 1
            
            logger.info(f"Generated {rca_count} new RCA reports")
            return rca_count
            
        except Exception as e:
            logger.error(f"Error running RCA batch: {e}")
            return 0
