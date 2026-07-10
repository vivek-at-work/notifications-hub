from __future__ import annotations

import pytest
from notifications_common.types import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.repositories.application import ApplicationRepository
from app.secrets.aws_secrets import AwsSecretsService
from app.services.channel_config_service import (
    ApnsChannelConfigInput,
    ChannelConfigService,
    EmailChannelConfigInput,
    FcmChannelConfigInput,
    SmsChannelConfigInput,
)
from app.services.notification_category_service import NotificationCategoryService


class MockSecretsClient:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get_secret_value(self, *, SecretId: str) -> dict[str, str]:
        return {"SecretString": self.store[SecretId]}

    def put_secret_value(self, *, SecretId: str, SecretString: str) -> None:
        self.store[SecretId] = SecretString

    def create_secret(self, *, Name: str, SecretString: str) -> None:
        self.store[Name] = SecretString


@pytest.mark.asyncio
async def test_channel_config_service_all_channels(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    app_record = await app_repo.create(name="Tenant", slug="tenant")
    await db_session.flush()

    principal = AuthPrincipal(role=Role.TENANT_ADMIN, application_id=str(app_record.id))
    app_id = str(app_record.id)

    mock_client = MockSecretsClient()
    secrets = AwsSecretsService(client=mock_client)
    service = ChannelConfigService(db_session, app_id, secrets)

    email = await service.configure_email(
        principal,
        EmailChannelConfigInput(
            ses_region="us-east-1",
            from_address="noreply@example.com",
            credentials='{"smtp":"secret"}',
        ),
    )
    assert email.config["from_address"] == "noreply@example.com"
    assert email.secret_ref is not None

    sms = await service.configure_sms(
        principal,
        SmsChannelConfigInput(sns_region="us-west-2", credentials='{"key":"sms"}'),
    )
    assert sms.channel == Channel.SMS.value

    fcm = await service.configure_fcm(
        principal,
        FcmChannelConfigInput(project_id="proj-1", credentials='{"key":"fcm"}'),
    )
    assert fcm.config["project_id"] == "proj-1"

    apns = await service.configure_apns(
        principal,
        ApnsChannelConfigInput(
            bundle_id="com.example.app",
            team_id="TEAM",
            key_id="KEY",
            environment="sandbox",
            credentials="p8-key-content",
        ),
    )
    assert apns.config["bundle_id"] == "com.example.app"

    configs = await service.list_configs(principal)
    assert len(configs) == 4
    assert secrets.get_secret(email.secret_ref) == '{"smtp":"secret"}'


@pytest.mark.asyncio
async def test_notification_category_crud(db_session: AsyncSession) -> None:
    app_repo = ApplicationRepository(db_session)
    app_record = await app_repo.create(name="Tenant", slug="tenant-categories")
    await db_session.flush()

    principal = AuthPrincipal(role=Role.TENANT_ADMIN, application_id=str(app_record.id))
    service = NotificationCategoryService.build(db_session, str(app_record.id))

    created = await service.create_category(
        principal,
        key="marketing",
        name="Marketing",
        is_mandatory=False,
    )
    assert created.key == "marketing"

    updated = await service.update_category(
        principal,
        str(created.id),
        is_mandatory=True,
    )
    assert updated.is_mandatory is True

    categories = await service.list_categories(principal)
    assert len(categories) == 1
