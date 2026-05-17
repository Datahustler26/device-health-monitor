"""Tests for battery analyzer service."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.device import (
    Device, Telemetry, BatteryHistory, BatteryHealthState
)
from app.services.battery_analyzer import BatteryAnalyzer


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
    """Create sample device for testing."""
    device = Device(
        device_id="ZBR-TEST-001",
        device_name="Test Scanner",
        device_type="barcode_scanner",
        model="DS3678",
        firmware_version="01.02.03",
        serial_number="SN123456",
        location="Warehouse"
    )
    db.add(device)
    db.commit()
    return device


def test_battery_health_state_healthy():
    """Test healthy battery state determination."""
    state = BatteryAnalyzer.calculate_battery_health_state(
        battery_pct=80,
        degradation_pct=5,
        charge_cycles=100,
        temperature=25
    )
    assert state == BatteryHealthState.HEALTHY


def test_battery_health_state_warning():
    """Test warning battery state determination."""
    state = BatteryAnalyzer.calculate_battery_health_state(
        battery_pct=30,
        degradation_pct=5,
        charge_cycles=100,
        temperature=25
    )
    assert state == BatteryHealthState.WARNING


def test_battery_health_state_critical():
    """Test critical battery state determination."""
    state = BatteryAnalyzer.calculate_battery_health_state(
        battery_pct=15,
        degradation_pct=5,
        charge_cycles=100,
        temperature=25
    )
    assert state == BatteryHealthState.CRITICAL


def test_battery_health_state_degradation_critical():
    """Test critical state due to degradation."""
    state = BatteryAnalyzer.calculate_battery_health_state(
        battery_pct=50,
        degradation_pct=25,
        charge_cycles=100,
        temperature=25
    )
    assert state == BatteryHealthState.CRITICAL


def test_battery_health_state_end_of_life():
    """Test end-of-life battery state."""
    state = BatteryAnalyzer.calculate_battery_health_state(
        battery_pct=50,
        degradation_pct=35,
        charge_cycles=501,
        temperature=25
    )
    assert state == BatteryHealthState.END_OF_LIFE


def test_analyze_device_battery(db, sample_device):
    """Test device battery analysis."""
    # Add telemetry
    telemetry = Telemetry(
        device_id=sample_device.device_id,
        battery_pct=75,
        temperature_celsius=25,
        connectivity_status="CONNECTED",
        firmware_version="01.02.03",
        charge_cycles=100,
        event_timestamp=datetime.utcnow(),
        event_id="evt-001"
    )
    db.add(telemetry)
    db.commit()
    
    # Analyze battery
    battery_history = BatteryAnalyzer.analyze_device_battery(db, sample_device.device_id)
    
    assert battery_history is not None
    assert battery_history.battery_pct == 75
    assert battery_history.state == BatteryHealthState.HEALTHY


def test_estimate_time_to_empty():
    """Test time-to-empty estimation."""
    time_minutes = BatteryAnalyzer.estimate_time_to_empty(
        battery_pct=50,
        recent_discharge_rate=10  # 10% per hour
    )
    
    assert time_minutes == 300  # 50% / 10% per hour * 60 minutes


def test_get_recent_discharge_rate(db, sample_device):
    """Test discharge rate calculation."""
    # Add telemetry readings
    base_time = datetime.utcnow()
    for i in range(5):
        telemetry = Telemetry(
            device_id=sample_device.device_id,
            battery_pct=100 - (i * 10),  # Decreasing battery
            temperature_celsius=25,
            connectivity_status="CONNECTED",
            firmware_version="01.02.03",
            charge_cycles=100,
            event_timestamp=base_time + timedelta(hours=i),
            event_id=f"evt-{i:03d}"
        )
        db.add(telemetry)
    db.commit()
    
    # Calculate discharge rate
    discharge_rate = BatteryAnalyzer.get_recent_discharge_rate(db, sample_device.device_id, hours=4)
    
    assert discharge_rate > 0
