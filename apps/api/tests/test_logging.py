from __future__ import annotations

import json
import logging

import pytest
from httpx import ASGITransport, AsyncClient

from app.logging import log_api, log_startup, setup_logging
from app.logging.sanitize import REDACTED, sanitize
from app.main import app


@pytest.fixture(autouse=True)
def reset_logging_state() -> None:
    import app.logging.emitters as emitters_module

    emitters_module._setup_complete = False
    app_logger = logging.getLogger("app")
    app_logger.handlers.clear()


def test_log_startup_emits_structured_record(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_level="INFO", log_format="json")
    log_startup(kind="app", action_name="startup", status="started")

    output = capsys.readouterr().err
    payload = json.loads(output.strip())
    assert payload["type"] == "startup"
    assert payload["detail"]["kind"] == "app"
    assert payload["detail"]["actionName"] == "startup"
    assert payload["detail"]["status"] == "started"


def test_log_api_emits_api_log(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_level="INFO", log_format="json")
    log_api(kind="graphql", message="query executed", operation="health")

    output = capsys.readouterr().err
    payload = json.loads(output.strip())
    assert payload["type"] == "api-log"
    assert payload["detail"]["kind"] == "graphql"


def test_sanitize_redacts_sensitive_values() -> None:
    payload = sanitize({"token": "secret-value", "path": "/graphql"})
    assert payload["token"] == REDACTED
    assert payload["path"] == "/graphql"


@pytest.mark.asyncio
async def test_health_request_is_not_http_logged(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_level="INFO", log_format="json")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200

    output = capsys.readouterr().err
    assert "http-log" not in output


@pytest.mark.asyncio
async def test_non_health_request_is_http_logged(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_level="INFO", log_format="json")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/version", headers={"x-request-id": "req-test-123"})
        assert response.status_code == 200
        assert response.headers["x-request-id"] == "req-test-123"

    output = capsys.readouterr().err
    lines = [json.loads(line) for line in output.strip().splitlines() if line.strip()]
    http_logs = [line for line in lines if line["type"] == "http-log"]
    assert len(http_logs) == 1
    assert http_logs[0]["detail"]["request_id"] == "req-test-123"
    assert http_logs[0]["detail"]["path"] == "/version"
