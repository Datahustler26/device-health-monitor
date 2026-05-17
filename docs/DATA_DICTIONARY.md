# Data Dictionary

## Devices Table

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | INT | Primary key | 1 |
| `device_id` | VARCHAR(50) | Unique device identifier | `ZBR-SC-00412` |
| `device_name` | VARCHAR(255) | Human-readable name | `Main Warehouse Scanner` |
| `device_type` | VARCHAR(100) | Device category | `barcode_scanner`, `printer`, `mobile_computer` |
| `model` | VARCHAR(100) | Manufacturer model | `DS3678`, `TC70` |
| `firmware_version` | VARCHAR(20) | Semantic version | `01.02.03` |
| `serial_number` | VARCHAR(100) | Manufacturer serial | `SN123456789` |
| `location` | VARCHAR(255) | Physical location | `Warehouse Zone A, Shelf 5` |
| `status` | VARCHAR(50) | Current status | `ACTIVE`, `INACTIVE`, `MAINTENANCE` |
| `created_at` | TIMESTAMP | Registration time | `2024-01-15T10:30:00Z` |
| `updated_at` | TIMESTAMP | Last update | `2024-01-20T15:45:00Z` |
| `last_seen` | TIMESTAMP | Last telemetry | `2024-01-20T15:44:59Z` |

---

## Telemetry Table

| Field | Type | Description | Range/Notes |
|-------|------|-------------|------------|
| `id` | INT | Primary key | |
| `device_id` | VARCHAR(50) | FK to devices | |
| `battery_pct` | FLOAT | Battery percentage | 0–100 |
| `temperature_celsius` | FLOAT | Device temp | -50 to 100°C |
| `humidity_pct` | FLOAT | Ambient humidity | 0–100 (optional) |
| `connectivity_status` | VARCHAR(20) | Network state | `CONNECTED`, `DISCONNECTED` |
| `signal_strength` | INT | WiFi/LTE strength | 0–100 (optional) |
| `charge_cycles` | INT | Total cycles | 0+ (optional) |
| `firmware_version` | VARCHAR(20) | Current FW | `01.02.03` |
| `uptime_seconds` | INT | Device uptime | 0+ (optional) |
| `memory_used_mb` | FLOAT | RAM usage | MB (optional) |
| `cpu_usage_pct` | FLOAT | CPU usage | 0–100 (optional) |
| `event_timestamp` | TIMESTAMP | Event time | Device-provided |
| `received_at` | TIMESTAMP | Ingestion time | Server time |
| `event_id` | VARCHAR(100) | Dedup ID | Unique per event |

**Indexes:** `(device_id, event_timestamp)`, `event_id` (unique)

---

## Battery History Table

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `id` | INT | Primary key | |
| `device_id` | VARCHAR(50) | FK to devices | |
| `battery_pct` | FLOAT | SoC snapshot | 0–100 |
| `state` | ENUM | Health state | `HEALTHY`, `WARNING`, `CRITICAL`, `END_OF_LIFE` |
| `degradation_pct` | FLOAT | Capacity lost | 0–100 |
| `charge_cycles` | INT | Total cycles | 0+ |
| `estimated_time_to_empty_minutes` | INT | TTEmpty | 0–1440 (optional) |
| `timestamp` | TIMESTAMP | Snapshot time | |

**State Rules:**
- **HEALTHY**: SoC ≥ 40%, degradation < 10%, temp normal
- **WARNING**: SoC 20–39% OR degradation 10–20% OR temp > 75°C
- **CRITICAL**: SoC < 20% OR degradation > 20% OR temp > 80°C
- **END_OF_LIFE**: cycles > 500 AND (100 - degradation) < 70%

---

## Alerts Table

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `id` | INT | Primary key | |
| `device_id` | VARCHAR(50) | FK to devices | |
| `alert_type` | VARCHAR(50) | Category | `BATTERY_CRITICAL`, `TEMP_BREACH`, `CONNECTIVITY_LOSS`, `FIRMWARE_EOL` |
| `severity` | ENUM | Priority level | `INFO`, `WARNING`, `CRITICAL` |
| `status` | ENUM | State | `ACTIVE`, `ACKNOWLEDGED`, `RESOLVED` |
| `message` | TEXT | Human text | `"Battery level critically low: 18%"` |
| `triggered_value` | FLOAT | Actual value | `18.5` (battery %), `85.2` (temp) |
| `threshold_value` | FLOAT | Trigger threshold | `20` (battery %), `80` (temp) |
| `created_at` | TIMESTAMP | Alert time | |
| `acknowledged_at` | TIMESTAMP | ACK time | (nullable) |
| `resolved_at` | TIMESTAMP | Resolution time | (nullable) |
| `resolution_notes` | TEXT | Post-mortem | `"Battery replaced with new unit"` |

**Alert Types:**
- `BATTERY_CRITICAL`: SoC < 20%
- `TEMP_BREACH`: Temperature outside operating range
- `CONNECTIVITY_LOSS`: No telemetry > 1 hour
- `FIRMWARE_EOL`: Firmware version deprecated

---

## RCA Reports Table

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | INT | Primary key | |
| `device_id` | VARCHAR(50) | FK to devices | `ZBR-SC-00412` |
| `alert_id` | INT | FK to alerts | (nullable) |
| `alert_type` | VARCHAR(50) | Alert category | `BATTERY_CRITICAL` |
| `probable_cause` | TEXT | Analysis output | `"Accelerated discharge: 12%/hr. Battery capacity at 61% of original."` |
| `recommended_action` | TEXT | Suggested fix | `"Schedule battery replacement within 7 days."` |
| `confidence_score` | FLOAT | 0.0–1.0 | `0.94` |
| `analysis_data` | TEXT | JSON details | `{"discharge_rate": 12.1, "cycles": 523, ...}` |
| `generated_at` | TIMESTAMP | Generation time | |

**Confidence Scoring:**
- 0.95–1.0: High confidence (multiple corroborating factors)
- 0.75–0.95: Moderate confidence (primary + secondary factors)
- 0.5–0.75: Low confidence (limited data)
- < 0.5: Insufficient data

---

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BATTERY_WARNING_THRESHOLD` | INT | 40 | SoC % for WARNING state |
| `BATTERY_CRITICAL_THRESHOLD` | INT | 20 | SoC % for CRITICAL state |
| `BATTERY_DEGRADATION_WARNING` | INT | 10 | Degradation % for WARNING |
| `BATTERY_DEGRADATION_CRITICAL` | INT | 20 | Degradation % for CRITICAL |
| `TEMP_MIN_THRESHOLD` | FLOAT | -20 | Min operating temp (°C) |
| `TEMP_MAX_THRESHOLD` | FLOAT | 80 | Max operating temp (°C) |
| `TEMP_WARNING_THRESHOLD` | FLOAT | 75 | Warning temp (°C) |
| `ANALYZER_INTERVAL_SECONDS` | INT | 300 | Battery analysis frequency |
| `RCA_INTERVAL_SECONDS` | INT | 600 | RCA generation frequency |

---

## Enumerations

### Device Status
```
ACTIVE       → Device operational and reporting
INACTIVE     → Device not reporting (> 24h silence)
MAINTENANCE  → Planned downtime
```

### Alert Status
```
ACTIVE         → Alert triggered, needs attention
ACKNOWLEDGED   → On-call acknowledged receipt
RESOLVED       → Issue fixed, alert closed
```

### Alert Severity
```
INFO        → Informational only
WARNING     → Attention recommended
CRITICAL    → Immediate action required
```

### Connectivity Status
```
CONNECTED      → Device has network connectivity
DISCONNECTED   → No network available
```
