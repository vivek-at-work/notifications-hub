from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    TEMPLATE_RENDER_ERROR = "TEMPLATE_RENDER_ERROR"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    CHANNEL_UNAVAILABLE = "CHANNEL_UNAVAILABLE"


class PlatformError(Exception):
    """Deterministic, machine-readable domain error."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field

    def to_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {"code": self.code.value, "message": self.message}
        if self.field is not None:
            payload["field"] = self.field
        return payload
