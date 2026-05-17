"""Tests for RCA engine."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.device import (
    Device, Telemetry, Alert, RCAReport, AlertSeverity, AlertStatus
)
from app.services.rca_engine import RCAEngine


@pytest.fixture
def db():
    """Create in-memory SQLite database for testing."""
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


def test_analyze_battery_critical_alert(db, sample_device):
    """Test RCA for battery critical alert."""
    # Add telemetry
    telemetry = Telemetry(
        device_id=sample_device.device_id,
        battery_pct=15,
        temperature_celsius=25,
        connectivity_status="CONNECTED",
        firmware_version="01.02.03",
        charge_cycles=100,
        event_timestamp=datetime.utcnow(),
        event_id="evt-001"
    )
    db.add(telemetry)
    
    # Create alert
    alert = Alert(
        device_id=sample_device.device_id,
        alert_type="BATTERY_CRITICAL",
        severity=AlertSeverity.CRITICAL,
        status=AlertStatus.ACTIVE,
        message="Battery level critical"
    )
    db.add(alert)
    db.commit()
    
    # Analyze
    rca_report = RCAEngine.analyze_alert(db, alert)
    
    assert rca_report is not None
    assert rca_report.alert_type == "BATTERY_CRITICAL"
    assert rca_report.confidence_score > 0


def test_analyze_temp_breach_alert(db, sample_device):
    """Test RCA for temperature breach alert."""
    # Add telemetry with high temperature
    telemetry = Telemetry(
        device_id=sample_device.device_id,
        battery_pct=75,
        temperature_celsius=85,
        connectivity_status="CONNECTED",
        firmware_version="01.02.03",
        charge_cycles=100,
        event_timestamp=datetime.utcnow(),
        event_id="evt-001"
    )
    db.add(telemetry)
    
    # Create alert
    alert = Alert(
        device_id=sample_device.device_id,
        alert_type="TEMP_BREACH",
        severity=AlertSeverity.WARNING,
        status=AlertStatus.ACTIVE,
        message="Temperature exceeded threshold"
    )
    db.add(alert)
    db.commit()
    
    # Analyze
    rca_report = RCAEngine.analyze_alert(db, alert)
    
    assert rca_report is not None
    assert "temperature" in rca_report.probable_cause.lower()
