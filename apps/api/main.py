from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apps.api.routers import (
    analysis_router,
    health_router,
    jobs_router,
    reports_router,
    ticker_router,
)
from packages.infra.cache.redis_client import cache_client
from packages.infra.config import settings
from packages.infra.db.session import init_db

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("financial_platform_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Financial Intelligence Platform API...")
    await init_db()
    await cache_client.connect()
    yield
    logger.info("Shutting down Financial Intelligence Platform API...")
    await cache_client.close()


app = FastAPI(
    title="Financial Intelligence Platform API",
    description=(
        "Production-grade multi-agent financial intelligence and reporting platform. "
        "Generates explainable, multi-source investment analysis reports backed by "
        "market data, financial statements, news intelligence, social sentiment, "
        "sector benchmarking, quantitative risk modeling, and multi-horizon forecasts."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("--> %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
        logger.info("<-- %s %s [Status %d]", request.method, request.url.path, response.status_code)
        return response
    except Exception as e:
        logger.error("Unhandled exception in request %s %s: %s", request.method, request.url.path, e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred while processing request."},
        )


# Register API Routers
app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(reports_router)
app.include_router(ticker_router)
app.include_router(jobs_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Financial Intelligence Platform",
        "version": "1.0.0",
        "phase": "Phase 1 - Monolith Foundation",
        "docs": "/docs",
    }
