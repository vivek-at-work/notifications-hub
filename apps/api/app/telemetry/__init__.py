from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


def setup_telemetry(app: FastAPI) -> None:
    """Configure OpenTelemetry instrumentation stubs for FastAPI."""

    # Full instrumentation wiring is added in observability milestone work.
    _ = app
