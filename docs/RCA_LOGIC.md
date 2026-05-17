# Root Cause Analysis Logic

## Overview

The RCA engine generates structured, confidence-scored reports when alerts fire. It correlates device telemetry with environmental factors and device history to identify root causes.

## RCA Rules by Alert Type

### 1. BATTERY_CRITICAL

**Trigger:** SoC < 20%

**Analysis Factors:**

| Factor | Weight | Rule |
|--------|--------|------|
| SoC Level | HIGH | < 10% → very critical |
| Discharge Rate | HIGH | > 10%/hour → accelerated drain |
| Degradation | MEDIUM | > 20% → aging battery |
| Charge Cycles | MEDIUM | > 500 → end-of-life |
| Temperature | MEDIUM | > 75°C → thermal stress |

**Decision Tree:**

```
IF (discharge_rate > 10%/hour AND battery_pct < 20%)
  THEN "Accelerated discharge detected"
       confidence += 0.2

IF (charge_cycles > 500 AND degradation > 20%)
  THEN "Battery at end-of-life"
       confidence = 0.95
       action = "Replace battery immediately"

IF (temperature > 80°C AND battery_pct < 20%)
  THEN "Thermal stress accelerating discharge"
       confidence += 0.15
       action = "Move to cooler location"

IF (no_degradation_history)
  THEN "Possible extreme discharge event"
       confidence = 0.6
       action = "Investigate usage patterns"
```

**Recommended Actions:**
- confidence >= 0.9: Battery replacement (urgent)
- 0.7–0.9: Battery replacement (within 24h)
- 0.5–0.7: Monitor discharge rate; replace if continues
- < 0.5: Investigate device for runaway processes

---

### 2. TEMP_BREACH

**Trigger:** Temperature < -20°C or > 80°C

**Analysis Factors:**

| Factor | Weight | Rule |
|--------|--------|------|
| Sustained Duration | HIGH | > 2 hours = environmental |
| Trend | MEDIUM | Rising temp = cooling failure |
| Device Location | MEDIUM | Check historical baseline |
| Humidity | LOW | May indicate equipment issue |

**Decision Tree:**

```
IF (temp_history[-1h] > threshold)
  AND (temp_trend = RISING)
  THEN "Sustained environmental heat"
       confidence = 0.9
       action = "Relocate device or improve ventilation"

IF (temp > threshold FOR < 5_min)
  THEN "Transient spike (possible direct sun)"
       confidence = 0.5
       action = "Monitor; may resolve naturally"

IF (device_location = OUTDOOR)
  AND (temp < -10 OR temp > 85)
  THEN "Operating outside design specs"
       confidence = 0.85
       action = "Move indoors or use protective enclosure"

IF (humidity > 80% AND temp > 75°C)
  THEN "High temp + humidity may cause condensation"
       confidence = 0.7
       action = "Ensure adequate ventilation"
```

**Recommended Actions:**
- confidence >= 0.85: Immediate relocation or cooling
- 0.7–0.85: Monitor; prepare to relocate
- 0.5–0.7: Investigate location conditions
- < 0.5: Possible sensor malfunction (validate manually)

---

### 3. CONNECTIVITY_LOSS

**Trigger:** No telemetry > 1 hour

**Analysis Factors:**

| Factor | Weight | Rule |
|--------|--------|------|
| Last Signal Strength | HIGH | Was it declining? |
| Power Status | HIGH | Battery was healthy? |
| Time of Day | MEDIUM | Scheduled maintenance? |
| Network Events | MEDIUM | WiFi outage? |

**Decision Tree:**

```
IF (last_battery_pct < 10)
  THEN "Device likely powered off due to low battery"
       confidence = 0.9
       action = "Charge device"

IF (signal_strength_trend = DECLINING)
  FOR last_30_minutes
  THEN "Gradual signal loss → moving/interference"
       confidence = 0.8
       action = "Check device location; reseat antenna"

IF (multiple_devices_offline)
  AND (same_location)
  THEN "Network outage affecting area"
       confidence = 0.95
       action = "Contact network team; escalate"

IF (device_status = MAINTENANCE)
  THEN "Planned downtime"
       confidence = 0.99
       action = "None - expected"

IF (all_other_factors_normal)
  THEN "Unknown connectivity issue"
       confidence = 0.6
       action = "Power cycle device; check logs"
```

**Recommended Actions:**
- confidence >= 0.9: Power-related or network outage
- 0.7–0.9: Signal loss or location change
- 0.5–0.7: Device issue; power cycle
- < 0.5: Check manual logs; validate sensor

---

### 4. FIRMWARE_EOL

**Trigger:** Firmware version in EOL list

**Analysis Factors:**

| Factor | Weight | Rule |
|--------|--------|------|
| Version Age | HIGH | Months since release |
| Security CVEs | HIGH | Known vulnerabilities |
| Feature Gaps | MEDIUM | Missing new capabilities |
| Support Status | HIGH | Officially unsupported |

**Decision Tree:**

```
IF (firmware_age > 180_days)
  AND (newer_version_available)
  THEN "Firmware deprecated"
       confidence = 0.95
       action = "Schedule firmware update"

IF (firmware_has_critical_cve)
  THEN "Security vulnerability"
       confidence = 0.99
       action = "Update immediately"

IF (firmware_new_major_version)
  AND (performance_improvements = TRUE)
  THEN "Significant improvements available"
       confidence = 0.8
       action = "Plan update in maintenance window"

IF (firmware_recent AND no_issues)
  THEN "Current version is stable"
       confidence = 0.0
       action = "No action needed"
```

**Recommended Actions:**
- confidence >= 0.95: Mandatory update
- 0.8–0.95: Schedule within 2 weeks
- 0.5–0.8: Schedule within month
- < 0.5: No immediate action; monitor

---

## Confidence Scoring

### Base Score Calculation

```
confidence = sum([
  factor1_weight * factor1_score,
  factor2_weight * factor2_score,
  ...
]) / sum([
  factor1_weight,
  factor2_weight,
  ...
])
```

### Factor Scores (0.0–1.0)

| Scenario | Score |
|----------|-------|
| Strong evidence (> 10 data points) | 0.95–1.0 |
| Moderate evidence (5–10 data points) | 0.70–0.95 |
| Limited evidence (< 5 data points) | 0.50–0.70 |
| Conflicting evidence | 0.30–0.50 |
| Insufficient data | < 0.30 |

### Adjustments

```
confidence *= recency_factor  # Newer data = higher weight
confidence *= corroboration_factor  # Multiple factors align
confidence = max(0.0, min(1.0, confidence))  # Clamp 0–1
```

---

## Data Collection Period

| Alert Type | Lookback | Resolution Time |
|-----------|----------|-----------------|
| BATTERY_CRITICAL | 24 hours | 5–10 min |
| TEMP_BREACH | 6 hours | 2–5 min |
| CONNECTIVITY_LOSS | 24 hours | 5–10 min |
| FIRMWARE_EOL | None (config-driven) | 1 min |

---

## Example RCA Report

```json
{
  "id": 42,
  "device_id": "ZBR-SC-00412",
  "alert_id": 128,
  "alert_type": "BATTERY_CRITICAL",
  "probable_cause": "Accelerated discharge rate detected (12%/hour). Battery capacity at 61% of original (degradation: 39%). Device has completed 523 charge cycles, exceeding design limit of 500.",
  "recommended_action": "Schedule battery replacement within 7 days. Device is in end-of-life phase.",
  "confidence_score": 0.94,
  "analysis_data": {
    "discharge_rate_pct_per_hour": 12.1,
    "battery_pct": 18.5,
    "degradation_pct": 39.2,
    "charge_cycles": 523,
    "temperature_celsius": 28.5,
    "analysis_period_hours": 24,
    "factors": {
      "accelerated_discharge": {"score": 0.95, "weight": 0.4},
      "battery_degradation": {"score": 0.9, "weight": 0.3},
      "charge_cycles": {"score": 0.95, "weight": 0.2},
      "thermal_stress": {"score": 0.5, "weight": 0.1}
    }
  },
  "generated_at": "2024-11-15T09:32:10Z"
}
```

---

## Extensions & Customization

To add new RCA rules:

1. Add analysis logic to `app/services/rca_engine.py`
2. Define new `_analyze_*` method
3. Add confidence scoring logic
4. Register in `analyze_alert()` dispatcher
5. Update this document
