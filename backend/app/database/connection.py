"""Async SQLAlchemy database connection."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None


def get_engine():
    """Lazy engine oluştur."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.LOG_LEVEL == "DEBUG",
        )
        logger.info(f"[DB] Engine created: {settings.DATABASE_URL}")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Async session factory döndür."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def get_db() -> AsyncSession:
    """FastAPI Depends() için async session generator."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def create_tables() -> None:
    """Tüm tabloları oluştur (startup'ta çağrılır)."""
    from app.database.models import Base
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("[DB] Tables created")
