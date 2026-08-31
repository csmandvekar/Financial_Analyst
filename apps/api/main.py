from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from apps.api.routers import (
    analysis_router,
    evaluation_router,
    health_router,
    jobs_router,
    reports_router,
    ticker_router,
)
from packages.infra.cache.redis_client import cache_client
from packages.infra.config import settings
from packages.infra.db.session import init_db
from packages.infra.observability.logging import configure_structured_logging
from packages.infra.observability.metrics import HTTP_REQUEST_DURATION_SECONDS
from packages.infra.observability.tracer import get_current_trace_id, tracer

# Initialize structured logging
configure_structured_logging(level=settings.LOG_LEVEL)
logger = logging.getLogger("financial_platform_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Financial Intelligence Platform API with OpenTelemetry & Metrics...")
    await init_db()
    await cache_client.connect()
    yield
    logger.info("Shutting down Financial Intelligence Platform API...")
    await cache_client.close()


app = FastAPI(
    title="Financial Intelligence Platform API",
    description=(
        "Production-grade multi-agent financial intelligence and reporting platform. "
        "Includes OpenTelemetry distributed tracing, Prometheus metrics, and offline "
        "backtesting evaluation framework."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# OpenTelemetry FastAPI Auto-Instrumentation
FastAPIInstrumentor.instrument_app(app, tracer_provider=None)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    """HTTP middleware recording Prometheus request latency histogram and structured logging."""
    start_time = time.perf_counter()
    path = request.url.path
    method = request.method
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        logger.error("Unhandled exception in request %s %s: %s", method, path, e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred while processing request."},
        )
    finally:
        duration_s = time.perf_counter() - start_time
        # Record Prometheus metric
        if not path.startswith("/metrics"):
            try:
                HTTP_REQUEST_DURATION_SECONDS.labels(
                    route=path, method=method, status=str(status_code)
                ).observe(duration_s)
            except Exception:
                pass


# Register API Routers
app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(reports_router)
app.include_router(ticker_router)
app.include_router(jobs_router)
app.include_router(evaluation_router)


@app.get("/metrics", tags=["Observability"], summary="Prometheus Metrics Endpoint")
async def metrics():
    """Exposes Prometheus scrape target for system, agent, cache, and business metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Financial Intelligence Platform",
        "version": "1.0.0",
        "phase": "Phase 2 - Observability, Testing & Evaluation",
        "docs": "/docs",
        "metrics": "/metrics",
    }
