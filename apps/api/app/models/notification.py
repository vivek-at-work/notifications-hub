from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.end_user import ApplicationUser


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_application_id_created_at", "application_id", "created_at"),
        Index("ix_notifications_application_id_status", "application_id", "status"),
        UniqueConstraint(
            "application_id",
            "idempotency_key",
            name="uq_notifications_application_id_idempotency_key",
        ),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    template_key: Mapped[str] = mapped_column(String(128), nullable=False)
    channels: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )
    placeholders: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    category_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    workflow_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    application: Mapped[Application] = relationship(back_populates="notifications")
    recipients: Mapped[list[NotificationRecipient]] = relationship(back_populates="notification")
    attempts: Mapped[list[NotificationAttempt]] = relationship(back_populates="notification")
    events: Mapped[list[NotificationEvent]] = relationship(back_populates="notification")


class NotificationRecipient(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "notification_recipients"

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_type: Mapped[str] = mapped_column(String(32), nullable=False)
    recipient_value: Mapped[str] = mapped_column(String(512), nullable=False)
    application_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("application_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    notification: Mapped[Notification] = relationship(back_populates="recipients")
    application_user: Mapped[ApplicationUser | None] = relationship()


class NotificationAttempt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notification_attempts"
    __table_args__ = (Index("ix_notification_attempts_provider_message_id", "provider_message_id"),)

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)

    notification: Mapped[Notification] = relationship(back_populates="attempts")


class NotificationEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "notification_events"

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    notification: Mapped[Notification] = relationship(back_populates="events")
