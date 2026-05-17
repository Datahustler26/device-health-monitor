"""Sample telemetry fixtures for testing."""

import json

SAMPLE_TELEMETRY_EVENTS = [
    {
        "device_id": "ZBR-SC-00001",
        "battery_pct": 85,
        "temperature_celsius": 22,
        "humidity_pct": 45,
        "connectivity_status": "CONNECTED",
        "signal_strength": 85,
        "charge_cycles": 150,
        "firmware_version": "01.02.03",
        "uptime_seconds": 86400,
        "memory_used_mb": 256,
        "cpu_usage_pct": 35,
        "event_id": "evt-2024-001-001"
    },
    {
        "device_id": "ZBR-SC-00002",
        "battery_pct": 45,
        "temperature_celsius": 28,
        "humidity_pct": 55,
        "connectivity_status": "CONNECTED",
        "signal_strength": 70,
        "charge_cycles": 320,
        "firmware_version": "01.02.02",
        "uptime_seconds": 172800,
        "memory_used_mb": 512,
        "cpu_usage_pct": 50,
        "event_id": "evt-2024-001-002"
    },
    {
        "device_id": "ZBR-SC-00003",
        "battery_pct": 18,
        "temperature_celsius": 35,
        "humidity_pct": 60,
        "connectivity_status": "CONNECTED",
        "signal_strength": 40,
        "charge_cycles": 520,
        "firmware_version": "01.02.01",
        "uptime_seconds": 259200,
        "memory_used_mb": 768,
        "cpu_usage_pct": 75,
        "event_id": "evt-2024-001-003"
    }
]


def load_sample_telemetry() -> list:
    """Load sample telemetry data."""
    return SAMPLE_TELEMETRY_EVENTS
