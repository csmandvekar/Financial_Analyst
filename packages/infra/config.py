from typing import Dict, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True

    # Database
    POSTGRES_USER: str = "financial_user"
    POSTGRES_PASSWORD: str = "financial_pass"
    POSTGRES_DB: str = "financial_intelligence"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://financial_user:financial_pass@localhost:5432/financial_intelligence"
    DATABASE_URL_SYNC: str = "postgresql://financial_user:financial_pass@localhost:5432/financial_intelligence"

    # SQLite fallback for test/dev environments without running Postgres
    USE_SQLITE_FALLBACK: bool = True
    SQLITE_URL: str = "sqlite+aiosqlite:///./financial_dev.db"

    # Cache (Redis)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_CACHE_FALLBACK: bool = True

    # External APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Forecast signal weights (sum must be 1.0)
    FORECAST_WEIGHT_FUNDAMENTAL: float = 0.35
    FORECAST_WEIGHT_SENTIMENT: float = 0.15
    FORECAST_WEIGHT_SECTOR: float = 0.25
    FORECAST_WEIGHT_MARKET: float = 0.25

    # Resilience defaults
    DEFAULT_TIMEOUT_SECONDS: float = 10.0
    MAX_RETRY_ATTEMPTS: int = 3
    CIRCUIT_BREAKER_FAIL_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: float = 30.0

    @property
    def forecast_weights(self) -> Dict[str, float]:
        return {
            "fundamental": self.FORECAST_WEIGHT_FUNDAMENTAL,
            "sentiment": self.FORECAST_WEIGHT_SENTIMENT,
            "sector": self.FORECAST_WEIGHT_SECTOR,
            "market": self.FORECAST_WEIGHT_MARKET,
        }


settings = Settings()
