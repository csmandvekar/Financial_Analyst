import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from packages.infra.config import settings
from packages.infra.db.models import Base

logger = logging.getLogger(__name__)

# Create sessionmaker singleton
AsyncSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


def _create_engine_for_url(url: str):
    if "sqlite" in url:
        return create_async_engine(
            url,
            echo=settings.DEBUG,
            future=True,
        )
    return create_async_engine(
        url,
        echo=settings.DEBUG,
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


engine = _create_engine_for_url(settings.DATABASE_URL)
AsyncSessionLocal.configure(bind=engine)


async def init_db() -> None:
    """Initialize database tables, falling back to SQLite if PostgreSQL is unreachable."""
    global engine
    try:
        # Re-check URL if settings were updated (e.g., in test mode)
        if str(engine.url) != settings.DATABASE_URL:
            engine = _create_engine_for_url(settings.DATABASE_URL)
            AsyncSessionLocal.configure(bind=engine)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully via %s", engine.url)
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK and "sqlite" not in str(engine.url):
            logger.warning(
                "Failed to connect to PostgreSQL (%s). Falling back to local SQLite: %s",
                e,
                settings.SQLITE_URL,
            )
            engine = _create_engine_for_url(settings.SQLITE_URL)
            AsyncSessionLocal.configure(bind=engine)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Initialized local SQLite fallback successfully.")
        else:
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding async db sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
