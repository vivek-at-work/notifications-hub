"""Shared domain types and utilities for notifications-hub."""

from notifications_common.errors import ErrorCode, PlatformError
from notifications_common.placeholders import PlaceholderRenderer, validate_placeholders
from notifications_common.types import (
    Channel,
    NotificationStatus,
    RecipientType,
)

__all__ = [
    "Channel",
    "ErrorCode",
    "NotificationStatus",
    "PlaceholderRenderer",
    "PlatformError",
    "RecipientType",
    "validate_placeholders",
]
