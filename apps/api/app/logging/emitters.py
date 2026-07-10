from __future__ import annotations

import logging
from typing import Any

from app.logging.context import get_request_id
from app.logging.sanitize import sanitize

_APP_LOGGER_NAME = "app"
_setup_complete = False


def setup_logging(*, log_level: str = "INFO", log_format: str = "text") -> None:
    global _setup_complete
    if _setup_complete:
        return

    app_logger = logging.getLogger(_APP_LOGGER_NAME)
    app_logger.handlers.clear()
    app_logger.setLevel(log_level.upper())
    app_logger.propagate = False

    from app.logging.formatters import StructuredLogFormatter

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogFormatter(use_json=log_format == "json"))
    app_logger.addHandler(handler)

    for logger_name in ("uvicorn", "sqlalchemy", "boto3", "botocore", "httpx", "urllib3"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    _setup_complete = True


def _emit(
    *,
    log_type: str,
    level: int,
    detail: dict[str, Any],
) -> None:
    logger = logging.getLogger(_APP_LOGGER_NAME)
    request_id = get_request_id()
    record = logger.makeRecord(
        logger.name,
        level,
        "(structured)",
        0,
        "",
        (),
        None,
    )
    record.log_type = log_type
    record.detail = sanitize(detail)
    if request_id:
        record.request_id = request_id
    logger.handle(record)


def log_startup(
    *,
    kind: str,
    action_name: str,
    status: str,
    **extra: Any,
) -> None:
    _emit(
        log_type="startup",
        level=logging.INFO,
        detail={
            "kind": kind,
            "actionName": action_name,
            "status": status,
            **extra,
        },
    )


def log_http(
    *,
    request_id: str,
    method: str,
    path: str,
    status: int,
    client_ip: str,
    duration_us: int,
    **extra: Any,
) -> None:
    _emit(
        log_type="http-log",
        level=logging.INFO,
        detail={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status": status,
            "client_ip": client_ip,
            "duration_us": duration_us,
            **extra,
        },
    )


def log_api(
    *,
    kind: str,
    message: str,
    level: int = logging.INFO,
    **extra: Any,
) -> None:
    _emit(
        log_type="api-log",
        level=level,
        detail={
            "kind": kind,
            "message": message,
            **extra,
        },
    )


def log_background_job(
    *,
    status: str,
    duration_us: int | None = None,
    request_id: str | None = None,
    **extra: Any,
) -> None:
    detail: dict[str, Any] = {"status": status, **extra}
    if duration_us is not None:
        detail["duration_us"] = duration_us
    if request_id is not None:
        detail["request_id"] = request_id
    _emit(
        log_type="background-job-log",
        level=logging.INFO,
        detail=detail,
    )
