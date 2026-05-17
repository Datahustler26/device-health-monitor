"""Tests for alert manager."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.db.session import Base
from app.models.device import (
    Device, Alert, AlertSeverity, AlertStatus
)
from app.services.alert_manager import AlertManager


@pytest.fixture
def db():
    """Create in-memory database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_device(db):
    """Create sample device."""
    device = Device(
        device_id="ZBR-TEST-001",
        device_name="Test Scanner",
        device_type="barcode_scanner",
        model="DS3678",
        firmware_version="01.02.03",
        serial_number="SN123456"
    )
    db.add(device)
    db.commit()
    return device


def test_create_alert(db, sample_device):
    """Test alert creation."""
    alert = AlertManager.create_alert(
        db=db,
        device_id=sample_device.device_id,
        alert_type="BATTERY_CRITICAL",
        severity=AlertSeverity.CRITICAL,
        message="Battery level critical",
        triggered_value=15,
        threshold_value=20
    )
    
    assert alert.device_id == sample_device.device_id
    assert alert.alert_type == "BATTERY_CRITICAL"
    assert alert.status == AlertStatus.ACTIVE


def test_acknowledge_alert(db, sample_device):
    """Test alert acknowledgment."""
    # Create alert
    alert = AlertManager.create_alert(
        db=db,
        device_id=sample_device.device_id,
        alert_type="BATTERY_CRITICAL",
        severity=AlertSeverity.CRITICAL,
        message="Battery level critical"
    )
    
    # Acknowledge
    acknowledged = AlertManager.acknowledge_alert(db, alert.id)
    
    assert acknowledged.status == AlertStatus.ACKNOWLEDGED
    assert acknowledged.acknowledged_at is not None


def test_resolve_alert(db, sample_device):
    """Test alert resolution."""
    # Create alert
    alert = AlertManager.create_alert(
        db=db,
        device_id=sample_device.device_id,
        alert_type="BATTERY_CRITICAL",
        severity=AlertSeverity.CRITICAL,
        message="Battery level critical"
    )
    
    # Resolve
    resolved = AlertManager.resolve_alert(
        db=db,
        alert_id=alert.id,
        resolution_notes="Battery replaced"
    )
    
    assert resolved.status == AlertStatus.RESOLVED
    assert resolved.resolution_notes == "Battery replaced"
