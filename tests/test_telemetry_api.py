"""Tests for telemetry API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.db.session import Base, get_db
from app.models.device import Device
from app.main import app


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
def client(db):
    """Create test client."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


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


def test_create_device(client):
    """Test device creation endpoint."""
    response = client.post(
        "/api/v1/devices/",
        json={
            "device_id": "ZBR-NEW-001",
            "device_name": "New Scanner",
            "device_type": "barcode_scanner",
            "model": "DS3678",
            "firmware_version": "01.02.03",
            "serial_number": "SN654321",
            "location": "Warehouse"
        }
    )
    
    assert response.status_code == 201
    assert response.json()["device_id"] == "ZBR-NEW-001"


def test_get_device(client, sample_device):
    """Test get device endpoint."""
    response = client.get(f"/api/v1/devices/{sample_device.device_id}")
    
    assert response.status_code == 200
    assert response.json()["device_id"] == sample_device.device_id


def test_ingest_telemetry(client, sample_device):
    """Test telemetry ingestion."""
    response = client.post(
        "/api/v1/telemetry/ingest",
        json={
            "device_id": sample_device.device_id,
            "battery_pct": 75,
            "temperature_celsius": 25,
            "connectivity_status": "CONNECTED",
            "firmware_version": "01.02.03",
            "charge_cycles": 100,
            "event_id": "evt-001"
        }
    )
    
    assert response.status_code == 202
    assert response.json()["status"] == "ingested"


def test_ingest_invalid_battery(client, sample_device):
    """Test invalid battery percentage."""
    response = client.post(
        "/api/v1/telemetry/ingest",
        json={
            "device_id": sample_device.device_id,
            "battery_pct": 150,  # Invalid
            "temperature_celsius": 25,
            "connectivity_status": "CONNECTED",
            "firmware_version": "01.02.03",
            "event_id": "evt-001"
        }
    )
    
    assert response.status_code == 422
