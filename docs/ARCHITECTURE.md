# System Architecture

## Overview

The Device Health Monitoring System is designed as a distributed, scalable platform for real-time monitoring of enterprise hardware devices (barcode scanners, printers, mobile computers, etc.).

## Core Components

### 1. **Ingestion Layer (FastAPI)**
- RESTful API for device telemetry submission
- Input validation and data quality checks
- Event deduplication via `event_id`
- Supports high throughput (10,000+ events/hour)

### 2. **Data Storage (PostgreSQL)**
- **Devices table**: Device metadata, firmware, location
- **Telemetry table**: Time-series events (indexed by device_id, timestamp)
- **Alerts table**: Alert history and resolution tracking
- **Battery History**: Battery health snapshots
- **RCA Reports**: Root cause analysis records

### 3. **Analysis Engine (Services)**

#### Battery Analyzer
- **State tracking**: HEALTHY → WARNING → CRITICAL → END_OF_LIFE
- **Degradation calculation**: Based on charge cycles and historical SoC
- **Discharge rate estimation**: 4-hour rolling average
- **Time-to-empty prediction**: Based on current discharge rate

#### RCA Engine
- **Contextual analysis**: Correlates 24-hour telemetry history
- **Multi-factor detection**:
  - Battery acceleration patterns
  - Temperature trends
  - Connectivity loss patterns
  - Firmware EOL status
- **Confidence scoring**: 0.0–1.0 scale based on evidence strength

#### Alert Manager
- **Dynamic creation**: Based on threshold violations
- **Deduplication**: Prevents duplicate alerts for same condition
- **Dispatch routing**: Slack, Email, SMS (configurable)
- **Resolution tracking**: Notes and timestamp recorded

### 4. **Scheduler (APScheduler)**
- **Battery analysis job**: Every 5 minutes (configurable)
- **RCA generation job**: Every 10 minutes (configurable)
- **Background execution**: Non-blocking, isolated database sessions

### 5. **Observability**
- **OTEL instrumentation**: FastAPI routes, SQLAlchemy queries
- **Structured logging**: JSON format for log aggregators
- **Jaeger tracing**: Distributed request tracing
- **Metrics export**: Prometheus-compatible endpoints

## Data Flow

```
Device → POST /api/v1/telemetry/ingest
           ↓
      [Validation]
           ↓
      [Deduplication Check]
           ↓
      PostgreSQL (Telemetry)
           ↓
      [Background Scheduler]
           ↓
      Battery Analyzer ──→ BatteryHistory
           ↓
      Threshold Check ──→ Alert Creation ──→ Alert Dispatch (Slack/Email)
           ↓
      RCA Engine ──→ RCAReport
           ↓
      Alert Details API ← Dashboard/UI
```

## Scalability Considerations

1. **Database**
   - Connection pooling (20 connections default)
   - Indexed queries on (device_id, timestamp)
   - Telemetry retention policy (configurable)

2. **API**
   - Stateless design (horizontally scalable)
   - Load balanced via NGINX/HAProxy
   - Async request handling with Uvicorn workers

3. **Scheduler**
   - Single instance (prevents job duplication)
   - Database-backed coordination for multi-instance
   - Configurable job intervals

4. **Storage**
   - PostgreSQL with replication
   - Partitioning by device_id for large tables
   - Archive/purge strategy for old telemetry

## Security Architecture

```
Device ──→ API Gateway (TLS 1.3)
           ├─ OAuth 2.0 Bearer token
           └─ Rate limiting
               ↓
          API Server
          ├─ Input validation
          ├─ SQL injection prevention (ORM)
          └─ Role-based access control
              ↓
          Database (PostgreSQL)
          ├─ Connection encryption
          ├─ Row-level security
          └─ Audit logging
```

## Decision Records

### Why FastAPI?
- Native async support for I/O-bound telemetry ingestion
- Auto-generated OpenAPI documentation
- Built-in data validation (Pydantic)
- High performance (benchmarks: 10k+ req/sec)

### Why PostgreSQL?
- ACID guarantees for alert consistency
- Window functions for time-series analysis
- Distributed tracing support (native JSON)
- JSONB for flexible analysis_data storage

### Why APScheduler?
- In-process scheduling (no external dependency)
- Configurable job intervals
- Database-backed coordination for HA
- Easy integration with SQLAlchemy sessions

### Why Docker Compose?
- Local development mirrors production
- Includes Jaeger for observability
- Self-contained (no external setup needed)
- Easy scaling for testing

## High Availability

### For Production:
- **API**: Load-balanced cluster (3+ instances)
- **Database**: Primary + replicas with failover
- **Scheduler**: Leader election via database
- **Alerts**: Message queue (RabbitMQ/SQS) for reliability

### Health Checks:
- `/health` endpoint: Database + scheduler status
- Database: Periodic `SELECT 1` health probes
- Scheduler: Tracks last job execution time

## Monitoring & Observability

1. **Metrics**
   - Telemetry ingestion rate
   - Alert creation rate
   - Analysis job duration
   - Database query latency

2. **Logs**
   - Structured JSON format
   - Correlation IDs for request tracing
   - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

3. **Traces**
   - Jaeger integration via OTEL
   - Sampled at 10% (configurable)
   - Trace all slow queries (>100ms)
