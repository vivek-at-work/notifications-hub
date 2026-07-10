from __future__ import annotations

import pytest
from notifications_common.errors import ErrorCode, PlatformError
from notifications_common.types import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.repositories.application import ApplicationRepository
from app.services.template_service import TemplateService


@pytest.mark.asyncio
async def test_template_service_versioning_and_render(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    app_record = await app_repo.create(name="Tenant", slug="tenant-templates")
    await db_session.flush()

    app_id = str(app_record.id)
    principal = AuthPrincipal(role=Role.TENANT_ADMIN, application_id=app_id)
    service = TemplateService.build(db_session)

    schema = {
        "type": "object",
        "properties": {"orderId": {"type": "string"}, "userName": {"type": "string"}},
        "required": ["orderId", "userName"],
    }

    v1 = await service.create_version(
        principal,
        app_id,
        key="order_confirmation",
        channel=Channel.EMAIL.value,
        subject="Order {{orderId}} confirmed",
        body="Hi {{userName}}, your order is confirmed.",
        placeholders_schema=schema,
    )
    assert v1.version == 1
    assert v1.is_active is True

    v2 = await service.create_version(
        principal,
        app_id,
        key="order_confirmation",
        channel=Channel.EMAIL.value,
        subject="Order {{orderId}} confirmed (v2)",
        body="Hello {{userName}}, confirmed.",
        placeholders_schema=schema,
    )
    assert v2.version == 2
    assert v2.is_active is True

    active = await service.get_active_template(app_id, "order_confirmation", Channel.EMAIL.value)
    assert active.id == v2.id

    rendered = service.render(
        active,
        {"orderId": "ORD-123", "userName": "Alice"},
    )
    assert rendered.subject == "Order ORD-123 confirmed (v2)"
    assert rendered.body == "Hello Alice, confirmed."

    versions = await service.list_versions(
        principal,
        app_id,
        "order_confirmation",
        Channel.EMAIL.value,
    )
    assert len(versions) == 2

    await service.activate_version(principal, app_id, str(v1.id))
    active = await service.get_active_template(app_id, "order_confirmation", Channel.EMAIL.value)
    assert active.id == v1.id


@pytest.mark.asyncio
async def test_template_placeholder_validation(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    app_record = await app_repo.create(name="Tenant", slug="tenant-validation")
    await db_session.flush()

    app_id = str(app_record.id)
    principal = AuthPrincipal(role=Role.TENANT_ADMIN, application_id=app_id)
    service = TemplateService.build(db_session)

    template = await service.create_version(
        principal,
        app_id,
        key="otp",
        channel=Channel.SMS.value,
        subject=None,
        body="Your OTP is {{otp}}",
        placeholders_schema={
            "type": "object",
            "properties": {"otp": {"type": "string"}},
            "required": ["otp"],
        },
    )

    with pytest.raises(PlatformError) as exc_info:
        service.render(template, {})
    assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
