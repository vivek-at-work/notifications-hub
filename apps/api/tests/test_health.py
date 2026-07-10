from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import SEMVER_PATTERN


@pytest.mark.asyncio
async def test_health_returns_healthy(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_version_returns_semver(client: AsyncClient) -> None:
    response = await client.get("/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "api"
    assert SEMVER_PATTERN.match(payload["version"])
