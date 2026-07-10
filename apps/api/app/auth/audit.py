from __future__ import annotations

from typing import Any

from app.logging import log_api


def log_permission_denied(**detail: Any) -> None:
    log_api(
        kind="audit",
        message="Permission denied",
        level=40,
        **detail,
    )


def log_authentication_failure(**detail: Any) -> None:
    log_api(
        kind="audit",
        message="Authentication failed",
        level=40,
        **detail,
    )
