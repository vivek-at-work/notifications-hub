from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChannelConfig, Notification, Template
from app.repositories.application import ApplicationRepository
from app.repositories.channel_config import ChannelConfigRepository
from app.repositories.notification_category import NotificationCategoryRepository
from app.repositories.template import TemplateRepository


@pytest.mark.asyncio
async def test_application_default_retention_policy(db_session: AsyncSession) -> None:
    repo = ApplicationRepository(db_session)
    application = await repo.create(name="Acme", slug="acme")
    await db_session.commit()

    assert application.retention_policy == {"notification_history_days": 90}


@pytest.mark.asyncio
async def test_notification_indexes_and_idempotency_constraint(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    application = await app_repo.create(name="Acme", slug="acme-notifications")
    await db_session.flush()

    notification = Notification(
        application_id=application.id,
        status="queued",
        template_key="welcome",
        channels=["email"],
        idempotency_key="idem-123",
    )
    db_session.add(notification)
    await db_session.commit()

    duplicate = Notification(
        application_id=application.id,
        status="queued",
        template_key="welcome",
        channels=["email"],
        idempotency_key="idem-123",
    )
    db_session.add(duplicate)

    with pytest.raises(Exception):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_tenant_scoped_repository_filters_by_application_id(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    app_a = await app_repo.create(name="App A", slug="app-a")
    app_b = await app_repo.create(name="App B", slug="app-b")
    await db_session.flush()

    template_repo_a = TemplateRepository(db_session, app_a.id)
    template_repo_b = TemplateRepository(db_session, app_b.id)

    await template_repo_a.create(
        Template(
            application_id=app_a.id,
            key="welcome",
            channel="email",
            version=1,
            is_active=True,
            subject="Hello",
            body="Welcome {{name}}",
            placeholders_schema={"type": "object"},
        ),
    )
    await template_repo_b.create(
        Template(
            application_id=app_b.id,
            key="welcome",
            channel="email",
            version=1,
            is_active=True,
            subject="Hi",
            body="Welcome {{name}}",
            placeholders_schema={"type": "object"},
        ),
    )
    await db_session.commit()

    templates_a = await template_repo_a.list_all()
    templates_b = await template_repo_b.list_all()

    assert len(templates_a) == 1
    assert templates_a[0].subject == "Hello"
    assert len(templates_b) == 1
    assert templates_b[0].subject == "Hi"


@pytest.mark.asyncio
async def test_channel_config_and_category_crud(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    application = await app_repo.create(name="Acme", slug="acme-config")
    await db_session.flush()

    channel_repo = ChannelConfigRepository(db_session, application.id)
    category_repo = NotificationCategoryRepository(db_session, application.id)

    await channel_repo.create(
        ChannelConfig(
            application_id=application.id,
            channel="email",
            config={"from_address": "noreply@example.com"},
            secret_ref="arn:aws:secretsmanager:us-east-1:123:secret:email",
        ),
    )
    await category_repo.create(key="marketing", name="Marketing", is_mandatory=False)
    await db_session.commit()

    email_config = await channel_repo.get_by_channel("email")
    marketing = await category_repo.get_by_key("marketing")

    assert email_config is not None
    assert email_config.config["from_address"] == "noreply@example.com"
    assert marketing is not None
    assert marketing.name == "Marketing"


@pytest.mark.asyncio
async def test_tenant_scoped_repository_rejects_cross_tenant(
    db_session: AsyncSession,
) -> None:
    app_repo = ApplicationRepository(db_session)
    app_a = await app_repo.create(name="App A", slug="app-a-scope")
    app_b = await app_repo.create(name="App B", slug="app-b-scope")
    await db_session.flush()

    template_repo_a = TemplateRepository(db_session, app_a.id)
    foreign_template = Template(
        application_id=app_b.id,
        key="welcome",
        channel="email",
        version=1,
        is_active=True,
        subject="Hello",
        body="Body",
        placeholders_schema={},
    )

    with pytest.raises(ValueError, match="application_id must match repository scope"):
        await template_repo_a.add(foreign_template)
