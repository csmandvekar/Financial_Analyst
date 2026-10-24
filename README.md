# 📈 Financial Intelligence Platform

[![CI Pipeline](https://github.com/csmandvekar/Financial_Analyst/actions/workflows/ci.yml/badge.svg)](https://github.com/csmandvekar/Financial_Analyst/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.5-black.svg?logo=next.js)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker)](https://www.docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Test Suite](https://img.shields.io/badge/Tests-27%2F27%20Passed-success.svg)](tests/)

A production-grade, multi-agent financial intelligence and reporting platform designed for institutional-level equity analysis. The system orchestrates specialized quantitative, qualitative, and risk agents across market data, financial statements, news, social sentiment, and sector benchmarks to generate explainable, audited investment outlooks.

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Key Features & Agent Workflow](#-key-features--agent-workflow)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Local Setup & Development](#-local-setup--development)
  - [Option A: Lightweight Local Setup (SQLite + In-Memory Fallback)](#option-a-lightweight-local-setup-sqlite--in-memory-fallback)
  - [Option B: Full Stack Local Setup (Docker Compose)](#option-b-full-stack-local-setup-docker-compose)
- [Local Testing & Verification Commands](#-local-testing--verification-commands)
  - [1. Running Automated Pytest Suite](#1-running-automated-pytest-suite)
  - [2. Testing Individual Test Layers](#2-testing-individual-test-layers)
  - [3. Code Quality & Linting](#3-code-quality--linting)
  - [4. Frontend Build & Typecheck](#4-frontend-build--typecheck)
  - [5. Manual API Smoke Tests](#5-manual-api-smoke-tests)
- [Observability & Monitoring](#-observability--monitoring)
- [End-to-End Production Deployment Guide](#-end-to-end-production-deployment-guide)
  - [Deployment Architecture Options](#deployment-architecture-options)
  - [Strategy 1: Single-Host VPS Deployment (Docker Compose + Nginx + SSL)](#strategy-1-single-host-vps-deployment-docker-compose--nginx--ssl)
  - [Strategy 2: Cloud Managed Container Deployment (AWS ECS / GCP Cloud Run)](#strategy-2-cloud-managed-container-deployment-aws-ecs--gcp-cloud-run)
  - [Strategy 3: Frontend Deployment to Vercel / Cloudflare Pages](#strategy-3-frontend-deployment-to-vercel--cloudflare-pages)
- [Environment Variables Reference](#-environment-variables-reference)
- [Contributing & Architecture Decisions (ADRs)](#-contributing--architecture-decisions-adrs)
- [License](#-license)

---

## 🏛 Overview & Architecture

The platform is designed around strict engineering principles:
1. **Typed Data Contracts**: Agents never exchange free-form natural language or untyped dictionaries. Every communication boundary conforms to versioned [Pydantic V2](packages/contracts/) schemas.
2. **Deterministic Calculations First**: Financial ratios, technical indicators (SMA, RSI, annualized volatility), stress testing, and signal weighting are computed deterministically in Python before report synthesis.
3. **Resilience & Fault Tolerance**: Built-in circuit breakers, token-bucket rate limiters, retries with exponential backoff and jitter (`tenacity`), and graceful degradation when upstream external data sources are unavailable.
4. **End-to-End Auditability**: Every run produces an immutable trace recording execution latency, confidence scores, citation sources, degraded services, and agent status.
5. **Continuous Evaluation**: Built-in offline backtesting framework computing Brier calibration scores, directional hit rates, interval coverage, and price error metrics (MAE/RMSE).

### System Diagram

```
                                 ┌───────────────────────────────┐
                                 │     Client / Web UI           │
                                 │  Next.js 14 (App Router)      │
                                 │  TanStack Query + Tailwind    │
                                 └───────────────┬───────────────┘
                                                 │ HTTP / REST
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │      FastAPI Gateway          │
                                 │  Auth, Validation, OpenTelemetry│
                                 └───────────────┬───────────────┘
                                                 │
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │      LangGraph DAG Engine     │
                                 │  StateGraph Orchestration     │
                                 └───────────────┬───────────────┘
                                                 │
          ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
          ▼                  ▼                   ▼                   ▼                  ▼
   ┌──────────────┐   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   ┌──────────────┐
   │ Market Data  │   │  Financials  │    │     News     │    │  Sentiment   │   │    Sector    │
   │    Agent     │   │    Agent     │    │    Agent     │    │    Agent     │   │    Agent     │
   └──────┬───────┘   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   └──────┬───────┘
          └──────────────────┴───────────────────┼───────────────────┴──────────────────┘
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │   Data Validation Node        │
                                 │  (Schema Checks & Fallbacks)  │
                                 └───────────────┬───────────────┘
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │    Signal Generation Node     │
                                 │  (Bayesian Signal Fusion)     │
                                 └───────────────┬───────────────┘
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │          Risk Node            │
                                 │  (VaR, Stress Scenarios, Beta)│
                                 └───────────────┬───────────────┘
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │         Forecast Node         │
                                 │  (3m / 6m / 1y Probabilities) │
                                 └───────────────┬───────────────┘
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │       Report Synthesis        │
                                 │  (Executive Summary, Scenarios)│
                                 └───────────────┬───────────────┘
                                                 │
                                ┌────────────────┴────────────────┐
                                ▼                                 ▼
                   ┌─────────────────────────┐       ┌─────────────────────────┐
                   │       PostgreSQL        │       │       Redis Cache       │
                   │   System of Record      │       │   TTL-based Invalidation│
                   └─────────────────────────┘       └─────────────────────────┘
```

---

## 🤖 Key Features & Agent Workflow

The orchestration pipeline consists of 8 modular steps:

| Step / Agent | Responsibility | Output Contract |
|---|---|---|
| **Market Data Agent** | Fetches OHLCV bars, calculates SMA-20, SMA-50, RSI-14, and annualized volatility. | `MarketDataSchema` |
| **Financials Agent** | Extracts P/E, EV/EBITDA, Debt-to-Equity, Current Ratio, Operating Margins. | `FinancialsSchema` |
| **News Agent** | Collects company headlines and scores sentiment polarity with relevance decay. | `NewsSchema` |
| **Sentiment Agent** | Analyzes retail and social community velocity and sentiment dispersion. | `SentimentSchema` |
| **Sector Agent** | Benchmarks performance against industry peers and sector ETFs (e.g., XLK, SPY). | `SectorSchema` |
| **Data Validation** | Guarantees non-null schemas; marks degraded providers if external calls fail. | `ValidatedDataBundle` |
| **Signal Fusion** | Weighted Bayesian blend: Fundamental (35%), Sector (25%), Market (25%), Sentiment (15%). | `SignalOutputSchema` |
| **Risk & Forecast** | Computes Value-at-Risk (VaR), beta sensitivity, stress testing, and 3m/6m/1y horizon confidence. | `ForecastSchema` |
| **Report Generation** | Assembles executive summary, bull/bear investment theses, and audit citations. | `ReportSchema` |

---

## 📂 Project Structure

```
Financial_Analyst/
├── apps/
│   ├── api/                       # FastAPI application backend
│   │   ├── main.py                # Server entrypoint & middleware lifecycle
│   │   └── routers/               # Analysis, reports, evaluation, jobs, ticker routers
│   └── web/                       # Next.js 14 frontend web application
│       ├── src/app/               # App Router pages (/analyze, /reports, /jobs)
│       ├── src/components/        # Stepper, report cards, Recharts visualizations
│       └── src/lib/api.ts         # TypeScript API client & schema normalizers
├── packages/
│   ├── agents/                    # 8 specialized financial intelligence agents
│   │   ├── base.py                # Abstract BaseAgent with resilience & timing wrappers
│   │   ├── financials/            # Corporate balance sheet & ratios agent
│   │   ├── forecast/              # Multi-horizon forecast synthesis agent
│   │   ├── market_data/           # Price series & technical indicators agent
│   │   ├── news/                  # Headline analysis & news sentiment agent
│   │   ├── report/                # Executive narrative & scenario synthesis
│   │   ├── risk/                  # Stress scenarios & risk engine
│   │   ├── sector/                # Benchmark & peer comparison agent
│   │   └── sentiment/             # Social sentiment & retail interest agent
│   ├── contracts/                 # Pydantic V2 immutable data contracts
│   ├── evaluation/                # Offline backtesting, Brier score, MAE/RMSE engine
│   ├── infra/                     # DB session, Redis caching, resilience, Prometheus metrics
│   └── orchestrator/              # LangGraph StateGraph DAG definition and nodes
├── docker/
│   ├── docker-compose.yml         # Multi-service stack (Postgres, Redis, API, Prometheus, Grafana)
│   ├── Dockerfile.api             # Multi-stage production container for FastAPI
│   ├── grafana/                   # Pre-configured Grafana dashboards & provisioning
│   └── prometheus/                # Prometheus scrape configuration
├── tests/
│   ├── unit/                      # Math, indicators, ratios, resilience tests
│   ├── contract/                  # Pydantic schema validation tests
│   ├── integration/               # FastAPI endpoints & pipeline integration
│   ├── chaos/                     # Upstream provider failure & circuit breaker tests
│   └── load/                      # Concurrent multi-ticker pipeline execution
├── pyproject.toml                 # Python dependencies & build metadata
└── .env.example                   # Environment configuration template
```

---

## ⚙️ Prerequisites

Ensure you have installed:
- **Python 3.12+**
- **Node.js 18+** & **npm**
- **Git**
- *(Optional for full stack)* **Docker** & **Docker Compose**

---

## 🚀 Local Setup & Development

### Option A: Lightweight Local Setup (SQLite + In-Memory Fallback)

The codebase has built-in fallbacks: if PostgreSQL or Redis is not running, it automatically defaults to local SQLite (`financial_dev.db`) and in-memory caching. You can run the entire platform locally with zero external server dependencies!

#### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/csmandvekar/Financial_Analyst.git
cd Financial_Analyst

# Create and activate Python virtual environment
# On Linux / macOS:
python3.12 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install package in editable mode with development dependencies
pip install --upgrade pip
pip install -e ".[dev]"

# Create your local environment file
cp .env.example .env

# Start the FastAPI server
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will now be live at:
- **API Root**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Prometheus Metrics**: [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)

---

#### 2. Frontend Setup

Open a separate terminal:

```bash
cd Financial_Analyst/apps/web

# Install frontend dependencies
npm install

# Start the Next.js development server
npm run dev
```

The web dashboard is now accessible at [http://localhost:3001](http://localhost:3001).

---

### Option B: Full Stack Local Setup (Docker Compose)

To spin up the production-like stack including PostgreSQL 16, Redis 7, the FastAPI backend, Prometheus, and Grafana:

```bash
cd Financial_Analyst

# Copy environment variables
cp .env.example .env

# Build and start all services in detached mode
docker compose -f docker/docker-compose.yml up -d --build
```

#### Services Started:
| Service | URL | Credentials (if applicable) |
|---|---|---|
| **API Backend** | [http://localhost:8000](http://localhost:8000) | - |
| **API Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | - |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | - |
| **Grafana Dashboard** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` |
| **PostgreSQL** | `localhost:5432` | `financial_user` / `financial_pass` |
| **Redis** | `localhost:6379` | - |

To stop the services:
```bash
docker compose -f docker/docker-compose.yml down
```

---

## 🧪 Local Testing & Verification Commands

The test suite is structured around the test pyramid: Unit, Contract, Integration, Chaos/Fault-injection, and Load testing.

### 1. Running Automated Pytest Suite

Make sure your virtual environment is active:

```bash
# Run all 27 tests with verbose output
pytest

# Run tests with code coverage report
pytest --cov=packages --cov=apps --cov-report=term-missing
```

*(All 27 test cases will execute and validate against local fallback or running databases).*

---

### 2. Testing Individual Test Layers

You can target specific layers of the system:

```bash
# 1. Unit Tests (Technical indicators, financial ratios, resilience, signal fusion)
pytest tests/unit/ -v

# 2. Contract Tests (Pydantic V2 schema validations & probability constraints)
pytest tests/contract/ -v

# 3. Integration Tests (Full API endpoints, degraded pipelines, evaluation routes)
pytest tests/integration/ -v

# 4. Chaos & Fault-Injection Tests (Circuit breaker tripping, multi-source upstream failures)
pytest tests/chaos/ -v

# 5. Load & Concurrency Tests (Concurrent multi-ticker analysis jobs)
pytest tests/load/ -v
```

---

### 3. Code Quality & Linting

Ensure code conforms to formatting and type safety:

```bash
# Fast linting with Ruff
ruff check .

# Automatic fix with Ruff
ruff check . --fix

# Static Type Checking with Mypy
mypy packages/ apps/ --ignore-missing-imports
```

---

### 4. Frontend Build & Typecheck

In `apps/web`:

```bash
cd apps/web

# Run Next.js linter
npm run lint

# Validate TypeScript and compile production build
npm run build
```

---

### 5. Manual API Smoke Tests

You can test the running API endpoints directly using `curl` or PowerShell `Invoke-RestMethod`:

#### Health Check
```bash
curl -X GET http://127.0.0.1:8000/health
```
**Expected Response:**
```json
{"status":"healthy","database":"connected","redis":"connected"}
```

#### Ticker Market Snapshot
```bash
curl -X GET http://127.0.0.1:8000/ticker/AAPL
```

#### Run Multi-Agent Analysis
```bash
curl -X POST http://127.0.0.1:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "analysis_type": "quarterly_outlook"}'
```

#### Run Offline Backtest Simulation
```bash
curl -X POST http://127.0.0.1:8000/evaluation/backtest \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"], "lookback_days": 90, "horizon": "3m"}'
```

#### Fetch Evaluation Accuracy Metrics
```bash
curl -X GET http://127.0.0.1:8000/evaluation/metrics
```

---

## 📊 Observability & Monitoring

The platform includes built-in observability:
- **Prometheus Metrics Endpoint**: Accessible at `/metrics`. Tracks HTTP request durations, agent execution timings, cache hit/miss ratios, circuit breaker status, and forecast evaluation accuracy.
- **OpenTelemetry Auto-Instrumentation**: Distributed traces track requests from API gateway through LangGraph node executions.
- **Grafana Provisioning**: Pre-built dashboard configs under `docker/grafana/` visualize latency percentiles, error rates, and agent throughput.

---

## 🌐 End-to-End Production Deployment Guide

### Deployment Architecture Options

Depending on your infrastructure scale, you can choose one of two primary production patterns:

```
Pattern 1: Monolithic Containerized (Fastest, Cost-Effective)
[ Client Browser ] ──HTTPS──> [ Nginx Reverse Proxy / Cloudflare ]
                                  ├── /api/*   ──> [ FastAPI Container :8000 ]
                                  └── /*       ──> [ Next.js Container :3001 ]
                                                    │
                                      ┌─────────────┴─────────────┐
                                      ▼                           ▼
                           [ Managed Postgres ]          [ Managed Redis ]

Pattern 2: Decoupled Cloud Native (High Availability)
[ Vercel / Edge CDN ] ──── Next.js Frontend
       │
     HTTPS REST API
       ▼
[ AWS ALB / Cloudflare ]
       ▼
[ ECS Fargate / Cloud Run ] ─── FastAPI Containers (Auto-scaling)
       │
 ┌─────┴───────────────────┐
 ▼                         ▼
[ AWS RDS PostgreSQL ]    [ AWS ElastiCache Redis ]
```

---

### Strategy 1: Single-Host VPS Deployment (Docker Compose + Nginx + SSL)

Ideal for hosting on an AWS EC2 instance, DigitalOcean Droplet, Hetzner, or Linode ($10–$20/mo).

#### Step 1: Provision the Server
1. Launch an Ubuntu 22.04 LTS or 24.04 LTS instance with at least **2 vCPUs and 4GB RAM**.
2. Point your DNS records (e.g., `api.yourdomain.com` and `app.yourdomain.com`) to the server IP.
3. SSH into your server:
   ```bash
   ssh ubuntu@<SERVER_IP>
   ```

#### Step 2: Install Docker & Docker Compose
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### Step 3: Clone Code & Configure Environment
```bash
git clone https://github.com/csmandvekar/Financial_Analyst.git /opt/financial-intel
cd /opt/financial-intel

# Generate secure production passwords
cp .env.example .env
nano .env
```
Ensure you update:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `POSTGRES_PASSWORD=<STRONG_RANDOM_PASSWORD>`
- `DATABASE_URL=postgresql+asyncpg://financial_user:<STRONG_RANDOM_PASSWORD>@postgres:5432/financial_intelligence`
- External API keys (`ALPHA_VANTAGE_API_KEY`, etc.)

#### Step 4: Build & Launch with Docker Compose
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

#### Step 5: Setup Nginx Reverse Proxy with Let's Encrypt SSL
```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/financial-intel.conf`:
```nginx
server {
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and obtain SSL certificates:
```bash
sudo ln -s /etc/nginx/sites-available/financial-intel.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Issue free SSL certificates automatically
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com
```

---

### Strategy 2: Cloud Managed Container Deployment (AWS ECS / GCP Cloud Run)

For enterprise scalability with managed databases:

#### 1. Database & Cache Provisioning
- **Database**: AWS RDS for PostgreSQL 16 (or GCP Cloud SQL). Create a database named `financial_intelligence`.
- **Cache**: AWS ElastiCache for Redis 7 (or GCP Memorystore).

#### 2. Build & Push API Image to Container Registry
```bash
# Authenticate to AWS ECR or Docker Hub
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build the API Docker image
docker build -f docker/Dockerfile.api -t financial-intel-api:latest .

# Tag and push
docker tag financial-intel-api:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/financial-intel-api:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/financial-intel-api:latest
```

#### 3. Deploy to AWS ECS Fargate or GCP Cloud Run
- Deploy the image as a task / container service with 1 vCPU and 2GB RAM.
- Inject database credentials securely from **AWS Secrets Manager** or **GCP Secret Manager**.
- Set the container command:
  ```bash
  uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
- Attach an Application Load Balancer (ALB) with an ACM SSL certificate.

---

### Strategy 3: Frontend Deployment to Vercel / Cloudflare Pages

The Next.js frontend in `apps/web` is designed for zero-config deployment to Vercel:

1. Push your repository to GitHub.
2. In the [Vercel Dashboard](https://vercel.com), click **Add New Project** and import the repository.
3. Configure the project settings:
   - **Root Directory**: `apps/web`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Set the Environment Variable:
   - `NEXT_PUBLIC_API_URL`: `https://api.yourdomain.com`
5. Click **Deploy**. Vercel will provision an edge-optimized global deployment.

---

## 🔐 Environment Variables Reference

| Variable | Description | Default / Example | Required in Prod? |
|---|---|---|---|
| `ENVIRONMENT` | Runtime environment (`development`, `test`, `production`) | `development` | Yes |
| `DEBUG` | FastAPI debug log toggle | `false` | Yes |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` | Yes |
| `DATABASE_URL` | Async SQLAlchemy PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` | Yes |
| `REDIS_URL` | Redis instance connection URI | `redis://host:6379/0` | Yes |
| `USE_SQLITE_FALLBACK` | Automatically fall back to SQLite if PostgreSQL is unreachable | `true` in dev, `false` in prod | No |
| `USE_IN_MEMORY_CACHE_FALLBACK` | Fall back to in-memory dict cache if Redis is unreachable | `true` in dev, `false` in prod | No |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key (fallback synthetic mock if empty) | - | Optional |
| `NEWS_API_KEY` | NewsAPI key (fallback synthetic mock if empty) | - | Optional |
| `REDDIT_CLIENT_ID` | Reddit OAuth Client ID | - | Optional |
| `REDDIT_CLIENT_SECRET` | Reddit OAuth Client Secret | - | Optional |
| `OPENAI_API_KEY` | OpenAI API key for enhanced narrative synthesis | - | Optional |
| `GEMINI_API_KEY` | Google Gemini API key | - | Optional |
| `FORECAST_WEIGHT_FUNDAMENTAL`| Weight for fundamental financial ratio signal | `0.35` | No |
| `FORECAST_WEIGHT_SENTIMENT`  | Weight for news and social sentiment signal | `0.15` | No |
| `FORECAST_WEIGHT_SECTOR`     | Weight for peer and sector comparative signal | `0.25` | No |
| `FORECAST_WEIGHT_MARKET`     | Weight for market momentum & technical indicators | `0.25` | No |

---

## 📑 Contributing & Architecture Decisions (ADRs)

All structural decisions are documented in the [`docs/adr/`](docs/adr/) folder. Before introducing substantial changes to agent communication protocols, storage drivers, or orchestration logic, please create an Architectural Decision Record following the template in [`07_adr_process_and_templates.md`](07_adr_process_and_templates.md).

---

## 📄 License

This project is open-source and distributed under the [MIT License](LICENSE).