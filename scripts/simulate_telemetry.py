"""Simulate telemetry from devices for testing."""

import argparse
import random
import time
import requests
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_telemetry(device_count: int, duration_seconds: int):
    """Simulate telemetry events from devices."""
    
    api_url = "http://localhost:8000/api/v1/telemetry/ingest"
    start_time = time.time()
    event_count = 0
    error_count = 0
    
    # Device state tracking
    device_states = {}
    for i in range(device_count):
        device_id = f"ZBR-SC-{i+1:05d}"
        device_states[device_id] = {
            "battery_pct": random.uniform(20, 100),
            "charge_cycles": random.randint(50, 500),
            "temperature_celsius": random.uniform(15, 35)
        }
    
    logger.info(f"Starting telemetry simulation for {device_count} devices for {duration_seconds}s")
    
    try:
        while (time.time() - start_time) < duration_seconds:
            # Simulate data from random device
            device_id = f"ZBR-SC-{random.randint(1, device_count):05d}"
            state = device_states[device_id]
            
            # Realistic battery decay
            state["battery_pct"] = max(0, state["battery_pct"] - random.uniform(0.1, 2.0))
            if state["battery_pct"] < 5:
                state["battery_pct"] = 100  # Simulate device charge
                state["charge_cycles"] += 1
            
            # Temperature fluctuation
            state["temperature_celsius"] += random.uniform(-1, 1)
            state["temperature_celsius"] = max(-20, min(80, state["temperature_celsius"]))
            
            # Create telemetry event
            telemetry = {
                "device_id": device_id,
                "battery_pct": round(state["battery_pct"], 1),
                "temperature_celsius": round(state["temperature_celsius"], 1),
                "humidity_pct": random.uniform(30, 70),
                "connectivity_status": "CONNECTED" if random.random() > 0.05 else "DISCONNECTED",
                "signal_strength": random.randint(30, 100),
                "charge_cycles": state["charge_cycles"],
                "firmware_version": f"{random.randint(0,1):02d}.{random.randint(0,9):02d}.{random.randint(0,9):02d}",
                "uptime_seconds": random.randint(3600, 259200),
                "memory_used_mb": random.uniform(100, 900),
                "cpu_usage_pct": random.uniform(5, 95),
                "event_id": f"evt-{device_id}-{int(time.time() * 1000)}-{random.randint(0, 999):03d}"
            }
            
            try:
                response = requests.post(api_url, json=telemetry, timeout=5)
                if response.status_code in [202, 200]:
                    event_count += 1
                    if event_count % 100 == 0:
                        logger.info(f"Ingested {event_count} events ({error_count} errors)")
                else:
                    error_count += 1
                    logger.warning(f"API error {response.status_code}: {response.text[:100]}")
            except requests.RequestException as e:
                error_count += 1
                if error_count == 1:
                    logger.error(f"Cannot connect to API at {api_url}. Start server with: docker-compose up")
                    return
            
            # Small delay between events
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        logger.info("Simulation interrupted")
    
    elapsed = time.time() - start_time
    rate = event_count / elapsed if elapsed > 0 else 0
    logger.info(f"✅ Simulation complete: {event_count} events in {elapsed:.1f}s ({rate:.0f} ev/s, {error_count} errors)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate device telemetry")
    parser.add_argument("--devices", type=int, default=50, help="Number of devices to simulate")
    parser.add_argument("--duration", type=int, default=300, help="Simulation duration in seconds")
    args = parser.parse_args()
    
    simulate_telemetry(args.devices, args.duration)
