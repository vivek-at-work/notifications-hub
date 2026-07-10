"""Initial notification platform schema.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-07-10
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "retention_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{\"notification_history_days\": 90}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "end_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("google_sub", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_sub"),
    )

    op.create_table(
        "application_api_keys",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_api_keys_application_id", "application_api_keys", ["application_id"])

    op.create_table(
        "application_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("end_user_id", sa.Uuid(), nullable=False),
        sa.Column("external_user_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["end_user_id"], ["end_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "external_user_id",
            name="uq_application_users_app_external_user",
        ),
    )
    op.create_index("ix_application_users_application_id", "application_users", ["application_id"])
    op.create_index("ix_application_users_end_user_id", "application_users", ["end_user_id"])

    op.create_table(
        "channel_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("secret_ref", sa.String(length=512), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "channel", name="uq_channel_configs_app_channel"),
    )
    op.create_index("ix_channel_configs_application_id", "channel_configs", ["application_id"])

    op.create_table(
        "device_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("application_user_id", sa.Uuid(), nullable=False),
        sa.Column("end_user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_user_id"], ["application_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["end_user_id"], ["end_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "token", name="uq_device_tokens_app_token"),
    )
    op.create_index("ix_device_tokens_application_id", "device_tokens", ["application_id"])
    op.create_index("ix_device_tokens_application_user_id", "device_tokens", ["application_user_id"])
    op.create_index("ix_device_tokens_end_user_id", "device_tokens", ["end_user_id"])

    op.create_table(
        "notification_categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "key", name="uq_notification_categories_app_key"),
    )
    op.create_index("ix_notification_categories_application_id", "notification_categories", ["application_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("template_key", sa.String(length=128), nullable=False),
        sa.Column("channels", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("placeholders", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("category_key", sa.String(length=128), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("correlation_id", sa.String(length=255), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workflow_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "idempotency_key",
            name="uq_notifications_application_id_idempotency_key",
        ),
    )
    op.create_index("ix_notifications_application_id", "notifications", ["application_id"])
    op.create_index(
        "ix_notifications_application_id_created_at",
        "notifications",
        ["application_id", "created_at"],
    )
    op.create_index(
        "ix_notifications_application_id_status",
        "notifications",
        ["application_id", "status"],
    )

    op.create_table(
        "templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("subject", sa.String(length=512), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("placeholders_schema", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "key",
            "channel",
            "version",
            name="uq_templates_app_key_channel_version",
        ),
    )
    op.create_index("ix_templates_application_id", "templates", ["application_id"])

    op.create_table(
        "user_channel_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("end_user_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["end_user_id"], ["end_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "end_user_id",
            "channel",
            name="uq_user_channel_preferences_app_user_channel",
        ),
    )
    op.create_index("ix_user_channel_preferences_application_id", "user_channel_preferences", ["application_id"])
    op.create_index("ix_user_channel_preferences_end_user_id", "user_channel_preferences", ["end_user_id"])

    op.create_table(
        "user_notification_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("end_user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["notification_categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["end_user_id"], ["end_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "end_user_id",
            "category_id",
            "channel",
            name="uq_user_notification_preferences_app_user_category_channel",
        ),
    )
    op.create_index(
        "ix_user_notification_preferences_application_id",
        "user_notification_preferences",
        ["application_id"],
    )
    op.create_index("ix_user_notification_preferences_end_user_id", "user_notification_preferences", ["end_user_id"])
    op.create_index("ix_user_notification_preferences_category_id", "user_notification_preferences", ["category_id"])

    op.create_table(
        "notification_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_message_id", sa.String(length=512), nullable=True),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_attempts_application_id", "notification_attempts", ["application_id"])
    op.create_index("ix_notification_attempts_notification_id", "notification_attempts", ["notification_id"])
    op.create_index(
        "ix_notification_attempts_provider_message_id",
        "notification_attempts",
        ["provider_message_id"],
    )

    op.create_table(
        "notification_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_events_application_id", "notification_events", ["application_id"])
    op.create_index("ix_notification_events_notification_id", "notification_events", ["notification_id"])

    op.create_table(
        "notification_recipients",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("recipient_type", sa.String(length=32), nullable=False),
        sa.Column("recipient_value", sa.String(length=512), nullable=False),
        sa.Column("application_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_user_id"], ["application_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_recipients_application_id", "notification_recipients", ["application_id"])
    op.create_index("ix_notification_recipients_notification_id", "notification_recipients", ["notification_id"])


def downgrade() -> None:
    op.drop_table("notification_recipients")
    op.drop_table("notification_events")
    op.drop_table("notification_attempts")
    op.drop_table("user_notification_preferences")
    op.drop_table("user_channel_preferences")
    op.drop_table("templates")
    op.drop_table("notifications")
    op.drop_table("notification_categories")
    op.drop_table("device_tokens")
    op.drop_table("channel_configs")
    op.drop_table("application_users")
    op.drop_table("application_api_keys")
    op.drop_table("end_users")
    op.drop_table("applications")
