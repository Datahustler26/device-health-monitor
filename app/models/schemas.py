"""Pydantic schemas for API requests/responses."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class BatteryHealthState(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    END_OF_LIFE = "END_OF_LIFE"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


# Device Schemas
class DeviceBase(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=50)
    device_name: str = Field(..., max_length=255)
    device_type: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    firmware_version: str = Field(..., max_length=20)
    serial_number: str = Field(..., max_length=100)
    location: str = Field(default="Unknown", max_length=255)


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    location: Optional[str] = None
    firmware_version: Optional[str] = None
    status: Optional[str] = None


class DeviceResponse(DeviceBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True


# Telemetry Schemas
class TelemetryBase(BaseModel):
    battery_pct: float = Field(..., ge=0, le=100)
    temperature_celsius: float = Field(..., ge=-50, le=100)
    connectivity_status: str
    firmware_version: str = Field(..., max_length=20)
    charge_cycles: Optional[int] = None
    humidity_pct: Optional[float] = None
    signal_strength: Optional[int] = None
    uptime_seconds: Optional[int] = None
    memory_used_mb: Optional[float] = None
    cpu_usage_pct: Optional[float] = None


class TelemetryIngest(TelemetryBase):
    device_id: str = Field(..., min_length=1, max_length=50)
    event_timestamp: Optional[datetime] = None
    event_id: str = Field(..., description="Unique event ID for deduplication")


class TelemetryResponse(TelemetryBase):
    id: int
    device_id: str
    event_timestamp: datetime
    received_at: datetime

    class Config:
        from_attributes = True


# Battery Health Schemas
class BatteryHealthResponse(BaseModel):
    device_id: str
    battery_pct: float
    state: BatteryHealthState
    degradation_pct: float
    charge_cycles: int
    estimated_time_to_empty_minutes: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    alert_type: str
    severity: AlertSeverity
    message: str
    triggered_value: Optional[float] = None
    threshold_value: Optional[float] = None


class AlertResponse(AlertBase):
    id: int
    device_id: str
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]

    class Config:
        from_attributes = True


class AlertResolve(BaseModel):
    resolution_notes: str = Field(..., max_length=500)


# RCA Report Schemas
class RCAReportResponse(BaseModel):
    id: int
    device_id: str
    alert_type: str
    probable_cause: str
    recommended_action: str
    confidence_score: float
    generated_at: datetime

    class Config:
        from_attributes = True


# Fleet Summary Schemas
class FleetSummaryResponse(BaseModel):
    total_devices: int
    active_devices: int
    inactive_devices: int
    healthy_batteries: int
    warning_batteries: int
    critical_batteries: int
    active_alerts_count: int
    devices_with_critical_alerts: int
    avg_battery_pct: float
    avg_temperature: float
    connectivity_rate: float


# Health Check Response
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    database_status: str
    scheduler_status: str
    version: str
