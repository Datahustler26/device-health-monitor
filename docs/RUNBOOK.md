# On-Call Runbook

## Common Incidents & Resolution

### 🚨 Alert: BATTERY_CRITICAL

**Symptoms:**
- Device battery < 20%
- Multiple devices failing simultaneously

**Investigation:**
```bash
# 1. Check fleet summary
curl http://localhost:8000/api/v1/health/fleet/summary

# 2. Get specific device battery analysis
curl http://localhost:8000/api/v1/health/devices/{DEVICE_ID}/battery

# 3. View recent telemetry
curl http://localhost:8000/api/v1/telemetry/{DEVICE_ID}?hours=24

# 4. Check RCA report
curl http://localhost:8000/api/v1/health/devices/{DEVICE_ID}/rca
```

**Actions:**
1. Acknowledge alert: `POST /api/v1/alerts/{ALERT_ID}/acknowledge`
2. If degradation > 20%: Schedule battery replacement
3. If discharge rate > 10%/hour: Check for runaway processes
4. If thermal cause: Check device location, cooling

**Resolution:**
```bash
# After replacement/fix
curl -X POST http://localhost:8000/api/v1/alerts/{ALERT_ID}/resolve \
  -H "Content-Type: application/json" \
  -d '{"resolution_notes": "Battery replaced - new unit shows 98% health"}'
```

---

### 🌡️ Alert: TEMP_BREACH

**Symptoms:**
- Device temperature > 80°C or < -20°C
- Usually device-specific, not fleet-wide

**Investigation:**
```bash
# Get temperature trend
curl http://localhost:8000/api/v1/telemetry/{DEVICE_ID}?hours=6

# Check location/environment
curl http://localhost:8000/api/v1/devices/{DEVICE_ID}
```

**Actions:**
1. Locate device (check `location` field)
2. Verify environmental controls (AC, heating)
3. Check for blocked vents or sun exposure
4. If sustained: Move device to cooler area

---

### 🔗 Alert: CONNECTIVITY_LOSS

**Symptoms:**
- Device not reporting for > 1 hour
- Last telemetry is stale

**Investigation:**
```bash
# Get device info
curl http://localhost:8000/api/v1/devices/{DEVICE_ID}

# Check last_seen timestamp
# If > 1 hour ago → connectivity issue
```

**Actions:**
1. Power cycle device (30 seconds)
2. Check network connectivity (ping device IP)
3. Verify DNS/gateway settings
4. Check WiFi signal strength in device UI
5. If persistent: Network team escalation

---

### 💻 Alert: API Performance Degradation

**Symptoms:**
- Response times > 500ms
- High error rate (>1%)

**Investigation:**
```bash
# Check database connection pool
# Check slow query log
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

# Check scheduler job queue
SELECT * FROM apscheduler.scheduled_jobs;
```

**Actions:**
1. Check database CPU/memory
2. Kill long-running queries if necessary
3. Disable battery analysis temporarily: `SCHEDULER_ENABLED=false`
4. Scale API instances if load is high

---

## Maintenance Tasks

### Daily
- Review active alerts count (goal: <10)
- Check fleet battery distribution (should be 70% HEALTHY)
- Monitor error logs (goal: <0.1% error rate)

### Weekly
- Audit resolution notes for patterns
- Review RCA accuracy (validate top 5 reports)
- Backup database

### Monthly
- Review telemetry retention (purge > 90 days if needed)
- Firmware update check (flagged by RCA engine)
- Capacity planning (device count trend)

---

## Emergency Procedures

### Service Restart
```bash
# Stop all services
docker-compose down

# Start with fresh scheduler
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### Database Recovery
```bash
# Restore from backup
docker exec dhm-postgres psql -U dhm_user -d device_health_db < backup.sql

# Run migrations
docker exec dhm-fastapi alembic upgrade head
```

### Clear Alert Backlog
```bash
# Mark old ACTIVE alerts as AUTO_RESOLVED
# (only if telemetry shows normal after 24h)
UPDATE alerts 
SET status = 'RESOLVED', resolved_at = NOW()
WHERE status = 'ACTIVE' 
AND created_at < NOW() - INTERVAL 24 HOURS;
```

---

## Escalation Matrix

| Alert Type | P1 Threshold | P2 Threshold | Owner |
|-----------|-------------|-------------|-------|
| BATTERY_CRITICAL | 50+ devices | 10+ devices | Device Ops |
| TEMP_BREACH | 20+ devices | 5+ devices | Facilities + Ops |
| CONNECTIVITY_LOSS | 100+ devices | 25+ devices | Network |
| API Degradation | Error rate >10% | Error rate >5% | Backend Eng |

---

## Contact Info

- **On-Call Phone:** [+1-XXX-XXX-XXXX](tel:+1-XXX-XXX-XXXX)
- **Slack Channel:** #device-health-monitoring
- **PagerDuty:** [Link]
- **Dashboard:** http://monitoring.company.com
