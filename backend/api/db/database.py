"""
Database engine, session factory, and initialization utilities.
Uses SQLAlchemy async for FastAPI compatibility.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import logging

from ..config import settings

logger = logging.getLogger(__name__)

import re

def _normalize_db_url(url: str) -> str:
    """Convert Supabase/Railway URL formats to SQLAlchemy async format."""
    if not url:
        return ""
    # postgres:// → postgresql+asyncpg://
    url = re.sub(r'^postgres://', 'postgresql+asyncpg://', url)
    url = re.sub(r'^postgresql://', 'postgresql+asyncpg://', url)
    return url

def _get_connect_args(url: str) -> dict:
    """Get asyncpg connect_args for SSL and pgbouncer compatibility."""
    if not url:
        return {}
    if 'supabase.co' in url or 'pooler.supabase' in url:
        return {
            'ssl': 'require',
            'prepared_statement_cache_size': 0,  # required for Supabase pgbouncer
        }
    return {}

# Async engine
db_url = _normalize_db_url(settings.database_url)
engine = create_async_engine(
    db_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=_get_connect_args(settings.database_url),
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Run on application startup — verify connection."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection established")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        # Don't crash — allow app to start with degraded DB
