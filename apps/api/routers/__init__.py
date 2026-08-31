from apps.api.routers.analysis import router as analysis_router
from apps.api.routers.evaluation import router as evaluation_router
from apps.api.routers.health import router as health_router
from apps.api.routers.jobs import router as jobs_router
from apps.api.routers.reports import router as reports_router
from apps.api.routers.ticker import router as ticker_router

__all__ = [
    "analysis_router",
    "evaluation_router",
    "health_router",
    "jobs_router",
    "reports_router",
    "ticker_router",
]
