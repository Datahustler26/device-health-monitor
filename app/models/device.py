"""Database models for Device Health Monitoring System."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.session import Base


class BatteryHealthState(str, enum.Enum):
    """Battery health states."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    END_OF_LIFE = "END_OF_LIFE"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    """Alert status."""
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class Device(Base):
    """Device model."""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True)
    device_name = Column(String(255))
    device_type = Column(String(100))  # e.g., "barcode_scanner", "printer"
    model = Column(String(100))
    firmware_version = Column(String(20))
    serial_number = Column(String(100))
    location = Column(String(255))
    status = Column(String(50), default="ACTIVE")  # ACTIVE, INACTIVE, MAINTENANCE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    telemetry = relationship("Telemetry", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    battery_history = relationship("BatteryHistory", back_populates="device", cascade="all, delete-orphan")
    rca_reports = relationship("RCAReport", back_populates="device", cascade="all, delete-orphan")


class Telemetry(Base):
    """Telemetry event model."""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), index=True)
    battery_pct = Column(Float)
    temperature_celsius = Column(Float)
    humidity_pct = Column(Float, nullable=True)
    connectivity_status = Column(String(20))  # CONNECTED, DISCONNECTED
    signal_strength = Column(Integer, nullable=True)  # 0-100
    charge_cycles = Column(Integer, nullable=True)
    firmware_version = Column(String(20))
    uptime_seconds = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    cpu_usage_pct = Column(Float, nullable=True)
    event_timestamp = Column(DateTime, index=True)
    received_at = Column(DateTime, default=datetime.utcnow, index=True)
    event_id = Column(String(100), unique=True, index=True)  # For deduplication
    
    device = relationship("Device", back_populates="telemetry")


class BatteryHistory(Base):
    """Battery health history tracking."""
    __tablename__ = "battery_history"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), index=True)
    battery_pct = Column(Float)
    state = Column(Enum(BatteryHealthState), default=BatteryHealthState.HEALTHY)
    degradation_pct = Column(Float)  # Percentage of capacity lost
    charge_cycles = Column(Integer)
    estimated_time_to_empty_minutes = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    device = relationship("Device", back_populates="battery_history")


class Alert(Base):
    """Alert model."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), index=True)
    alert_type = Column(String(50))  # BATTERY_CRITICAL, TEMP_BREACH, etc.
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    message = Column(Text)
    triggered_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    device = relationship("Device", back_populates="alerts")


class RCAReport(Base):
    """Root Cause Analysis report."""
    __tablename__ = "rca_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    alert_type = Column(String(50))
    probable_cause = Column(Text)
    recommended_action = Column(Text)
    confidence_score = Column(Float)  # 0.0 to 1.0
    analysis_data = Column(Text)  # JSON with analysis details
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    device = relationship("Device", back_populates="rca_reports")
