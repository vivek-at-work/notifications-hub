from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.end_user import EndUser


class NotificationCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notification_categories"
    __table_args__ = (
        UniqueConstraint("application_id", "key", name="uq_notification_categories_app_key"),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    application: Mapped[Application] = relationship(back_populates="categories")
    user_preferences: Mapped[list[UserNotificationPreference]] = relationship(
        back_populates="category"
    )


class UserNotificationPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_notification_preferences"
    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "end_user_id",
            "category_id",
            "channel",
            name="uq_user_notification_preferences_app_user_category_channel",
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
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notification_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    category: Mapped[NotificationCategory] = relationship(back_populates="user_preferences")
    end_user: Mapped[EndUser] = relationship(back_populates="notification_preferences")


class UserChannelPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_channel_preferences"
    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "end_user_id",
            "channel",
            name="uq_user_channel_preferences_app_user_channel",
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
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    end_user: Mapped[EndUser] = relationship(back_populates="channel_preferences")
