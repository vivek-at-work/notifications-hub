from __future__ import annotations

from enum import StrEnum


class Channel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH_ANDROID = "push_android"
    PUSH_IOS = "push_ios"


class NotificationStatus(StrEnum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecipientType(StrEnum):
    EMAIL = "email"
    PHONE = "phone"
    DEVICE_TOKEN = "device_token"
    USER_ID = "user_id"
