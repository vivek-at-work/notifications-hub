from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.end_user import EndUser
    from app.models.preference import UserChannelPreference, UserNotificationPreference


class EndUser(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "end_users"

    email: Mapped[str | None] = mapped_column(String(320), nullable=True, unique=True)
    google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    application_users: Mapped[list[ApplicationUser]] = relationship(back_populates="end_user")
    device_tokens: Mapped[list[DeviceToken]] = relationship(back_populates="end_user")
    notification_preferences: Mapped[list[UserNotificationPreference]] = relationship(
        back_populates="end_user",
    )
    channel_preferences: Mapped[list[UserChannelPreference]] = relationship(
        back_populates="end_user"
    )


class ApplicationUser(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "application_users"
    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "external_user_id",
            name="uq_application_users_app_external_user",
        ),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    end_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("end_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_user_id: Mapped[str] = mapped_column(String(255), nullable=False)

    application: Mapped[Application] = relationship(back_populates="application_users")
    end_user: Mapped[EndUser] = relationship(back_populates="application_users")
    device_tokens: Mapped[list[DeviceToken]] = relationship(back_populates="application_user")


class DeviceToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "device_tokens"
    __table_args__ = (
        UniqueConstraint("application_id", "token", name="uq_device_tokens_app_token"),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    application_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("application_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    end_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("end_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    token: Mapped[str] = mapped_column(String(512), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    application_user: Mapped[ApplicationUser] = relationship(back_populates="device_tokens")
    end_user: Mapped[EndUser] = relationship(back_populates="device_tokens")
