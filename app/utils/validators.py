"""Input validators."""

from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def validate_device_id(device_id: str) -> bool:
        """Validate device ID format."""
        if not device_id or len(device_id) > 50:
            return False
        return True
    
    @staticmethod
    def validate_battery_percentage(battery_pct: float) -> bool:
        """Validate battery percentage is 0-100."""
        return 0 <= battery_pct <= 100
    
    @staticmethod
    def validate_temperature(temp_celsius: float) -> bool:
        """Validate temperature is in operating range."""
        return -50 <= temp_celsius <= 100
    
    @staticmethod
    def validate_firmware_version(version: str) -> bool:
        """Validate semantic version format (X.Y.Z)."""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
    
    @staticmethod
    def validate_event_timestamp(timestamp: datetime) -> bool:
        """Validate event timestamp is fresh (< 1 hour old)."""
        if not timestamp:
            return True  # Default to current time
        
        age_seconds = (datetime.utcnow() - timestamp).total_seconds()
        return 0 <= age_seconds < 3600  # 1 hour
    
    @staticmethod
    def validate_event_id(event_id: str) -> bool:
        """Validate event ID for deduplication."""
        return bool(event_id) and len(event_id) <= 100
