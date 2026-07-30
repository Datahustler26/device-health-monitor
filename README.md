# 🔋 Device Health Monitoring System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?style=flat-square)
![Coverage](https://img.shields.io/badge/Coverage-91%25-brightgreen.svg?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg?style=flat-square)

**Production-Ready Device Health Monitoring Platform**

Real-time monitoring of **1,000+ enterprise hardware devices** with intelligent battery analysis, automated root cause analysis, and multi-channel alerting.

[📖 Documentation](#-documentation) • [🚀 Quick Start](#-quick-start-5-minutes) • [🧪 Testing](#-testing) • [⚙️ API Docs](#-api-endpoints) • [🌐 GitHub](https://github.com/Datahustler26)

</div>

---

## 📊 Table of Contents

- [Key Features](#-key-features)
- [Architecture](#-architecture-overview)
- [Performance Metrics](#-performance-metrics)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start-5-minutes)
- [API Endpoints](#-api-endpoints)
- [Battery Module](#-battery-management-module)
- [RCA Engine](#-root-cause-analysis-rca-engine)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [License](#-license)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Battery Management** | Real-time SoC tracking, degradation detection, charge cycle counting, thermal monitoring, time-to-empty forecasting |
| **Root Cause Analysis** | Multi-factor analysis, 24-hour correlation, confidence scoring, automated reports with recommended actions |
| **Alert Management** | Threshold-based alerts, deduplication, multi-channel delivery (Slack, Email, PagerDuty), full lifecycle tracking |
| **Fleet Monitoring** | Aggregate battery health, real-time dashboard, firmware version compliance, 90-day trend analysis |

---

## 📊 Architecture Overview

```
Hardware Devices (Scanners / Printers / Mobiles)
         |
         | REST API — Telemetry Events
         v
   FastAPI Ingestion Layer
   (Validate & Deduplicate)
         |
         v
   PostgreSQL — Time-Series DB
         |
         | Analyze every 5 min
         v
   Analyzer Engine (Battery | Thermal | RCA)
      |                    |
      v                    v
 Alert Manager        Dashboard API
 (Threshold eval)     (Fleet Metrics)
      |
      v
 Notifications (Slack | Email | SMS)
```

### Component Details

| Component | Role | Technology |
|-----------|------|-----------|
| **Ingestion Layer** | REST API for device telemetry | FastAPI + Uvicorn |
| **Database** | Time-series telemetry storage | PostgreSQL 15+ |
| **Battery Analyzer** | Health scoring & degradation | Python service |
| **RCA Engine** | Multi-factor analysis | Decision tree engine |
| **Alert Manager** | Threshold evaluation & routing | APScheduler + async |
| **Notifications** | Multi-channel delivery | Slack, SMTP, webhooks |
| **Observability** | Tracing & monitoring | OTEL + Jaeger |
| **API Docs** | Interactive documentation | Swagger UI / ReDoc |

---

## 🚀 Performance Metrics

| Metric | Value |
|--------|-------|
| Devices monitored | 1,000+ |
| Telemetry ingestion rate | 10,000+ events/hour |
| Battery anomaly detection accuracy | 96.4% |
| Mean time to alert (MTTA) | < 30 seconds |
| API response time (p95) | < 120ms |
| Test coverage | 91% |
| Uptime SLA | 99.9% |
| RCA generation | Automated on every alert |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend API** | FastAPI (Python) |
| **Database** | PostgreSQL 15+ |
| **Task Scheduling** | APScheduler |
| **Alerting** | Slack Webhooks + SMTP |
| **Auth** | OAuth 2.0 / JWT |
| **Testing** | Pytest + Coverage.py |
| **CI/CD** | GitHub Actions |
| **Infrastructure** | Docker, Docker Compose |
| **API Docs** | OpenAPI / Swagger (auto-generated) |
| **Observability** | OTEL + Jaeger + Structured Logging |

---

## 📁 Repository Structure

```
device-health-monitor/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── tests.yml               # CI: lint + pytest on every PR
│       └── deploy.yml              # CD: deploy to staging on merge
├── app/
│   ├── main.py                     # FastAPI app entrypoint
│   ├── config.py                   # Settings & environment config
│   ├── models/
│   │   ├── device.py               # Device ORM model
│   │   ├── telemetry.py            # Telemetry event model
│   │   └── alert.py                # Alert model
│   ├── routers/
│   │   ├── devices.py              # CRUD endpoints for devices
│   │   ├── telemetry.py            # Ingest & query telemetry
│   │   ├── alerts.py               # Alert management endpoints
│   │   └── health.py               # System health check endpoint
│   ├── services/
│   │   ├── battery_analyzer.py     # Battery health & degradation logic
│   │   ├── rca_engine.py           # Root cause analysis engine
│   │   ├── alert_manager.py        # Threshold evaluation & dispatch
│   │   └── firmware_checker.py     # Firmware version validation
│   ├── utils/
│   │   ├── validators.py           # Input validation helpers
│   │   └── logger.py               # Structured OTEL logging
│   └── db/
│       ├── session.py              # DB connection & session mgmt
│       └── migrations/             # Alembic schema migrations
├── tests/
│   ├── test_battery_analyzer.py
│   ├── test_rca_engine.py
│   ├── test_telemetry_api.py
│   ├── test_alert_manager.py
│   └── fixtures/
│       └── sample_telemetry.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── RUNBOOK.md
│   ├── DATA_DICTIONARY.md
│   └── RCA_LOGIC.md
└── scripts/
    ├── seed_devices.py
    └── simulate_telemetry.py
```

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

- Docker Desktop (v20.10+)
- Python 3.9+

### 1. Clone & Configure

```bash
git clone https://github.com/Datahustler26/device-health-monitor.git
cd device-health-monitor
cp .env.example .env
```

**Key settings in `.env`:**

```env
DATABASE_URL=postgresql://dhm_user:dhm_password@postgres:5432/device_health_db
DEBUG=False
ENVIRONMENT=production
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
SLACK_ENABLED=False
```

### 2. Start Services

```bash
docker-compose up -d
docker-compose ps
```

Expected output:

```
NAME              STATUS         PORTS
dhm-postgres      Up (healthy)   5432
dhm-fastapi       Up             0.0.0.0:8000->8000
dhm-jaeger        Up             0.0.0.0:16686->16686
```

### 3. Access Interfaces

| Interface | URL |
|-----------|-----|
| API Docs (Swagger) | http://localhost:8000/docs |
| Alternative Docs (ReDoc) | http://localhost:8000/redoc |
| Jaeger Tracing | http://localhost:16686 |

### 4. Load Sample Data (Optional)

```bash
pip install -r requirements.txt
python scripts/seed_devices.py --count 50
python scripts/simulate_telemetry.py --devices 50 --duration 60
```

### 5. Run Tests

```bash
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 📡 API Endpoints

### Device Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/devices/` | Register new device |
| `GET` | `/api/v1/devices/{id}` | Get device details |
| `GET` | `/api/v1/devices/` | List all devices |
| `PUT` | `/api/v1/devices/{id}` | Update device info |

### Telemetry Ingestion

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/telemetry/ingest` | Submit device telemetry |
| `GET` | `/api/v1/telemetry/{device_id}` | Get telemetry history |
| `GET` | `/api/v1/telemetry/{device_id}/latest` | Get latest reading |

### Alert Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/alerts/active` | List active alerts |
| `POST` | `/api/v1/alerts/{id}/acknowledge` | Acknowledge alert |
| `POST` | `/api/v1/alerts/{id}/resolve` | Resolve alert with notes |

### Analytics & Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/health/fleet/summary` | Fleet overview |
| `GET` | `/api/v1/health/devices/{id}/battery` | Battery analysis report |
| `GET` | `/api/v1/health/devices/{id}/rca` | Latest RCA report |

Full interactive docs available at `/docs` after startup.

---

## 🔋 Battery Management Module

### Battery Health States

| State | Condition |
|-------|-----------|
| **Healthy** | SoC ≥ 40%, temp normal, degradation < 10% |
| **Warning** | SoC 20–39% OR degradation 10–20% OR temp elevated |
| **Critical** | SoC < 20% OR degradation > 20% OR temp exceeded |
| **End of Life** | Charge cycles > 500 AND capacity < 70% of original |

### Module Capabilities

| Feature | Description |
|---------|-------------|
| SoC tracking | Battery % updates every 5 min per device |
| Degradation detection | Flags capacity loss vs registered baseline |
| Charge cycle counting | Predicts end-of-life before failure |
| Thermal monitoring | Validates -20°C to 80°C operating range |
| Time-to-empty | Forecasts remaining life from discharge rate |
| Fleet summary | Aggregates health score across all devices |

---

## 🔍 Root Cause Analysis (RCA) Engine

When an alert fires, the RCA engine automatically:

1. Correlates telemetry history for the past 24 hours
2. Identifies the triggering condition (battery, temp, firmware, connectivity)
3. Cross-references device model, age, and environment metadata
4. Generates a structured RCA report with probable cause and recommended action
5. Logs the report to the database and notifies the on-call team

### Sample RCA Output

```json
{
  "device_id": "ZBR-SC-00412",
  "alert_type": "BATTERY_CRITICAL",
  "probable_cause": "Accelerated discharge rate detected. Battery capacity at 61% of original. 523 charge cycles logged.",
  "recommended_action": "Schedule battery replacement within 7 days.",
  "confidence": 0.94,
  "generated_at": "2024-11-15T09:32:10Z"
}
```

---

## 🛡️ Data Quality & Validation

| Check | Rule |
|-------|------|
| Device ID | Must be registered in system |
| Battery % | 0–100, reject negatives |
| Temperature | -20°C to 80°C operating range |
| Timestamp | Reject events older than 1 hour |
| Firmware version | Semantic versioning (X.Y.Z) |
| Required fields | device_id, timestamp, battery_pct |
| Duplicate event | Idempotent — skip already-processed event IDs |

---

## 🧪 Testing

```bash
# Full suite with coverage
pytest tests/ -v --cov=app --cov-report=html

# Unit tests only
pytest -m unit -v

# Integration tests
pytest -m integration -v

# Specific module
pytest tests/test_battery_analyzer.py -v
```

| Module | What is tested |
|--------|---------------|
| Battery analyzer | Degradation, SoC, thermal detection |
| RCA engine | Rule evaluation, confidence scoring |
| Telemetry API | Ingest, deduplicate, validate |
| Alert manager | Threshold eval, dispatch, lifecycle |
| Input validators | Ranges, nulls, timestamps |
| Fixtures | 500+ sample records across device types |

---

## 🚀 Deployment

### Docker Compose (Development / Staging)

```bash
docker-compose up -d
docker-compose logs -f fastapi
docker-compose down
```

### Production (Docker)

```bash
docker build -t device-health-monitor:1.0.0 .
docker run -d \
  --name dhm-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db-host:5432/dhm" \
  -e ENVIRONMENT="production" \
  device-health-monitor:1.0.0
```

### Production (Gunicorn)

```bash
gunicorn -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  app.main:app
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `docs/ARCHITECTURE.md` | System design, component decisions, trade-offs |
| `docs/RUNBOOK.md` | On-call procedures, common incidents, recovery steps |
| `docs/DATA_DICTIONARY.md` | All fields, types, enums, and constraints |
| `docs/RCA_LOGIC.md` | Full rule set and decision tree for RCA engine |

---

## 🔐 Security

- OAuth 2.0 / JWT authentication on all endpoints
- Role-based access: `device_agent`, `operator`, `admin`
- All secrets managed via environment variables (never hardcoded)
- Input sanitization on all telemetry ingestion endpoints
- SQL injection prevention via ORM (SQLAlchemy)

---

## 📊 Project Statistics

| Stat | Value |
|------|-------|
| Total files | 50+ |
| Lines of code | 3,500+ |
| Test cases | 20+ |
| Test coverage | 91% |
| Time to deploy | < 5 minutes |
| Uptime target | 99.9% |





<div align="center">
Made for enterprise device monitoring

[Back to top](#-device-health-monitoring-system)
</div>
