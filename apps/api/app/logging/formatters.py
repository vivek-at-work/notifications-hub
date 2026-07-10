from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.logging.sanitize import sanitize


class StructuredLogFormatter(logging.Formatter):
    def __init__(self, *, use_json: bool) -> None:
        super().__init__()
        self.use_json = use_json

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "type": getattr(record, "log_type", "app"),
            "detail": sanitize(getattr(record, "detail", {})),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["detail"] = {**payload["detail"], "request_id": request_id}
        if self.use_json:
            return json.dumps(payload, default=str)
        detail = payload["detail"]
        detail_text = " ".join(f"{key}={value}" for key, value in detail.items())
        return f"{payload['timestamp']} {payload['level']} {payload['type']} {detail_text}"
