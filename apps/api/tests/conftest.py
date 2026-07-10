from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import re
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.oidc import OidcService
from app.db import create_tables, dispose_db, init_db, reset_db
from app.db.session import get_session_factory
from app.main import app

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


@pytest.fixture(scope="session")
def oidc_service() -> OidcService:
    return OidcService()


@pytest_asyncio.fixture
async def prepared_db() -> AsyncIterator[None]:
    reset_db(database_url=os.environ["DATABASE_URL"])
    init_db(os.environ["DATABASE_URL"])
    await create_tables()
    yield
    await dispose_db()
    reset_db()


@pytest_asyncio.fixture
async def db_session(prepared_db: None) -> AsyncIterator[AsyncSession]:
    factory = get_session_factory()
    async with factory() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def client(prepared_db: None) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
