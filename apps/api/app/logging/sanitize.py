from __future__ import annotations

from typing import Any

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "credential",
        "credentials",
    }
)

REDACTED = "***REDACTED***"


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_value(key, item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def _sanitize_value(key: str, value: Any) -> Any:
    normalized = key.lower().replace("-", "_")
    if normalized in SENSITIVE_KEYS:
        return REDACTED
    return sanitize(value)
