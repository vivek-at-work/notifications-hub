from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import SEMVER_PATTERN


@pytest.mark.asyncio
async def test_graphql_health_and_version(client: AsyncClient) -> None:
    response = await client.post(
        "/graphql",
        json={"query": "{ health version }"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["health"] == "healthy"
    assert SEMVER_PATTERN.match(payload["data"]["version"])


@pytest.mark.asyncio
async def test_graphql_echo_mutation(client: AsyncClient) -> None:
    response = await client.post(
        "/graphql",
        json={
            "query": 'mutation { echo(message: "test") }',
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["echo"] == "test"
