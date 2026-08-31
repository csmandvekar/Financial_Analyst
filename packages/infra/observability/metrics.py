from prometheus_client import Counter, Gauge, Histogram

# HTTP metrics
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["route", "method", "status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

# Agent execution metrics
AGENT_EXECUTION_DURATION_SECONDS = Histogram(
    "agent_execution_duration_seconds",
    "Agent execution duration in seconds",
    ["agent_name", "status"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0),
)

AGENT_EXECUTION_TOTAL = Counter(
    "agent_execution_total",
    "Total count of agent executions by status",
    ["agent_name", "status"],  # success, degraded, failed
)

# External API metrics
EXTERNAL_API_CALL_TOTAL = Counter(
    "external_api_call_total",
    "Total count of external API calls by source and status",
    ["source", "status"],
)

EXTERNAL_API_CALL_DURATION_SECONDS = Histogram(
    "external_api_call_duration_seconds",
    "External API call latency in seconds",
    ["source"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)

# Cache metrics
CACHE_HIT_TOTAL = Counter(
    "cache_hit_total",
    "Total number of cache hits by source prefix",
    ["cache_key_prefix"],
)

CACHE_MISS_TOTAL = Counter(
    "cache_miss_total",
    "Total number of cache misses by source prefix",
    ["cache_key_prefix"],
)

# Resilience metrics
CIRCUIT_BREAKER_STATE = Gauge(
    "circuit_breaker_state",
    "Current state of circuit breaker (0=closed, 1=open, 2=half_open)",
    ["source"],
)

# Forecast & Job business outcome metrics
FORECAST_CONFIDENCE_SCORE = Histogram(
    "forecast_confidence_score",
    "Forecast confidence score distributions",
    ["ticker", "horizon"],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

JOB_COMPLETION_TOTAL = Counter(
    "job_completion_total",
    "Total count of completed analysis jobs by outcome status",
    ["status"],  # completed, degraded, failed
)
