"""Battery health analyzer service."""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
import logging
from app.config import settings
from app.models.device import (
    Telemetry, BatteryHistory, BatteryHealthState, Device, Alert, AlertSeverity
)
from sqlalchemy import desc, and_

logger = logging.getLogger(__name__)


class BatteryAnalyzer:
    """Analyze battery health from telemetry data."""
    
    @staticmethod
    def calculate_battery_health_state(
        battery_pct: float,
        degradation_pct: float,
        charge_cycles: int,
        temperature: float
    ) -> BatteryHealthState:
        """Determine battery health state based on metrics."""
        
        # END_OF_LIFE: charge cycles > 500 AND capacity < 70%
        if charge_cycles > 500 and (100 - degradation_pct) < 70:
            return BatteryHealthState.END_OF_LIFE
        
        # CRITICAL: SoC < 20% OR degradation > 20% OR temp exceeded
        if (battery_pct < settings.battery_critical_threshold or
            degradation_pct > settings.battery_degradation_critical or
            temperature > settings.temp_max_threshold):
            return BatteryHealthState.CRITICAL
        
        # WARNING: SoC 20-39% OR degradation 10-20% OR temp elevated
        if (settings.battery_critical_threshold <= battery_pct < settings.battery_warning_threshold or
            settings.battery_degradation_warning <= degradation_pct <= settings.battery_degradation_critical or
            temperature > settings.temp_warning_threshold):
            return BatteryHealthState.WARNING
        
        # HEALTHY: meets all normal thresholds
        return BatteryHealthState.HEALTHY
    
    @staticmethod
    def calculate_degradation(db: Session, device_id: str) -> float:
        """Calculate battery degradation percentage."""
        
        # Get initial battery reading
        first_reading = db.query(Telemetry).filter(
            Telemetry.device_id == device_id
        ).order_by(Telemetry.event_timestamp).first()
        
        if not first_reading:
            return 0.0
        
        # Get latest reading
        latest_reading = db.query(Telemetry).filter(
            Telemetry.device_id == device_id
        ).order_by(desc(Telemetry.event_timestamp)).first()
        
        if not latest_reading:
            return 0.0
        
        # Degradation = (original_capacity - current_capacity) / original_capacity * 100
        # Approximated by comparing charge cycle capacity
        if first_reading.charge_cycles == 0:
            return 0.0
        
        # Assume 0.1% degradation per charge cycle
        degradation = min((latest_reading.charge_cycles or 0) * 0.1, 100.0)
        return degradation
    
    @staticmethod
    def estimate_time_to_empty(
        battery_pct: float,
        recent_discharge_rate: float
    ) -> Optional[int]:
        """Estimate time to empty in minutes based on discharge rate."""
        
        if recent_discharge_rate <= 0:
            return None
        
        # minutes = (current_battery % / discharge_rate %) * 60
        # Assuming discharge_rate is per hour
        time_to_empty = (battery_pct / recent_discharge_rate) * 60
        return max(0, int(time_to_empty))
    
    @staticmethod
    def get_recent_discharge_rate(db: Session, device_id: str, hours: int = 4) -> float:
        """Calculate discharge rate over recent hours."""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        readings = db.query(Telemetry).filter(
            and_(
                Telemetry.device_id == device_id,
                Telemetry.event_timestamp >= since
            )
        ).order_by(Telemetry.event_timestamp).all()
        
        if len(readings) < 2:
            return 0.0
        
        # Calculate average discharge rate
        first = readings[0]
        last = readings[-1]
        
        battery_drop = first.battery_pct - last.battery_pct
        if battery_drop <= 0:
            return 0.0
        
        time_diff = (last.event_timestamp - first.event_timestamp).total_seconds() / 3600  # hours
        if time_diff <= 0:
            return 0.0
        
        discharge_rate = battery_drop / time_diff  # % per hour
        return max(0.0, discharge_rate)
    
    @staticmethod
    def analyze_device_battery(db: Session, device_id: str) -> Optional[BatteryHistory]:
        """Perform comprehensive battery analysis for a device."""
        
        try:
            # Get latest telemetry
            latest_telemetry = db.query(Telemetry).filter(
                Telemetry.device_id == device_id
            ).order_by(desc(Telemetry.event_timestamp)).first()
            
            if not latest_telemetry:
                logger.warning(f"No telemetry found for device {device_id}")
                return None
            
            # Calculate metrics
            degradation = BatteryAnalyzer.calculate_degradation(db, device_id)
            discharge_rate = BatteryAnalyzer.get_recent_discharge_rate(db, device_id)
            time_to_empty = BatteryAnalyzer.estimate_time_to_empty(
                latest_telemetry.battery_pct,
                discharge_rate
            )
            
            # Determine health state
            health_state = BatteryAnalyzer.calculate_battery_health_state(
                latest_telemetry.battery_pct,
                degradation,
                latest_telemetry.charge_cycles or 0,
                latest_telemetry.temperature_celsius
            )
            
            # Create battery history record
            battery_history = BatteryHistory(
                device_id=device_id,
                battery_pct=latest_telemetry.battery_pct,
                state=health_state,
                degradation_pct=degradation,
                charge_cycles=latest_telemetry.charge_cycles or 0,
                estimated_time_to_empty_minutes=time_to_empty
            )
            
            db.add(battery_history)
            db.commit()
            
            logger.info(
                f"Battery analysis for {device_id}: "
                f"SoC={latest_telemetry.battery_pct}%, "
                f"degradation={degradation:.1f}%, "
                f"state={health_state.value}"
            )
            
            return battery_history
            
        except Exception as e:
            logger.error(f"Error analyzing battery for {device_id}: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def analyze_all_devices(db: Session) -> Dict[str, BatteryHistory]:
        """Analyze battery health for all active devices."""
        
        devices = db.query(Device).filter(Device.status == "ACTIVE").all()
        results = {}
        
        for device in devices:
            battery_analysis = BatteryAnalyzer.analyze_device_battery(db, device.device_id)
            if battery_analysis:
                results[device.device_id] = battery_analysis
        
        logger.info(f"Completed battery analysis for {len(results)} devices")
        return results
