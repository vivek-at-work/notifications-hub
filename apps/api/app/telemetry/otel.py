from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


def instrument_fastapi(app: FastAPI) -> None:
    """Stub for OpenTelemetry FastAPI instrumentation."""

    _ = app
