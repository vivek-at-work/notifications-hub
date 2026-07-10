from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.application_api_key import ApplicationApiKey
    from app.models.channel_config import ChannelConfig
    from app.models.end_user import ApplicationUser
    from app.models.notification import Notification
    from app.models.preference import NotificationCategory
    from app.models.template import Template

DEFAULT_RETENTION_POLICY: dict[str, Any] = {"notification_history_days": 90}


class Application(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    retention_policy: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=lambda: DEFAULT_RETENTION_POLICY.copy(),
        server_default='{"notification_history_days": 90}',
    )

    api_keys: Mapped[list[ApplicationApiKey]] = relationship(back_populates="application")
    channel_configs: Mapped[list[ChannelConfig]] = relationship(back_populates="application")
    templates: Mapped[list[Template]] = relationship(back_populates="application")
    notifications: Mapped[list[Notification]] = relationship(back_populates="application")
    categories: Mapped[list[NotificationCategory]] = relationship(back_populates="application")
    application_users: Mapped[list[ApplicationUser]] = relationship(back_populates="application")
