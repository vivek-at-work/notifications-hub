from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(settings.database_url, echo=False)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


def init_db(database_url: str | None = None) -> None:
    """Initialize engine from optional database URL override."""
    global _engine, _session_factory
    if database_url is not None:
        _engine = create_async_engine(database_url, echo=False)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    else:
        get_engine()
        get_session_factory()


async def create_tables() -> None:
    import app.models  # noqa: F401 — register models with metadata
    from app.db.base import Base

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


def reset_db(*, database_url: str | None = None) -> None:
    """Reset engine/session factory — used in tests."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None
    if database_url is not None:
        from app.config import get_settings

        get_settings.cache_clear()
        import os

        os.environ["DATABASE_URL"] = database_url


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
