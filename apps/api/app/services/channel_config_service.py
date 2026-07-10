from __future__ import annotations

import uuid
from dataclasses import dataclass

from notifications_common.errors import ErrorCode, PlatformError
from notifications_common.types import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authorization import require_application_access, require_role
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.models.channel_config import ChannelConfig
from app.repositories.channel_config import ChannelConfigRepository
from app.secrets.aws_secrets import AwsSecretsService


@dataclass(frozen=True, slots=True)
class EmailChannelConfigInput:
    ses_region: str
    from_address: str
    secret_ref: str | None = None
    credentials: str | None = None


@dataclass(frozen=True, slots=True)
class SmsChannelConfigInput:
    sns_region: str
    secret_ref: str | None = None
    credentials: str | None = None


@dataclass(frozen=True, slots=True)
class FcmChannelConfigInput:
    project_id: str
    secret_ref: str | None = None
    credentials: str | None = None


@dataclass(frozen=True, slots=True)
class ApnsChannelConfigInput:
    bundle_id: str
    team_id: str
    key_id: str
    environment: str
    secret_ref: str | None = None
    credentials: str | None = None


def _app_id(application_id: str) -> uuid.UUID:
    return uuid.UUID(application_id)


class ChannelConfigService:
    def __init__(
        self,
        session: AsyncSession,
        application_id: str,
        secrets_service: AwsSecretsService | None = None,
    ) -> None:
        self._application_id = application_id
        self._repository = ChannelConfigRepository(session, _app_id(application_id))
        self._secrets = secrets_service or AwsSecretsService()

    async def configure_email(
        self,
        principal: AuthPrincipal | None,
        config: EmailChannelConfigInput,
    ) -> ChannelConfig:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        secret_ref = self._resolve_secret_ref(
            channel=Channel.EMAIL.value,
            secret_ref=config.secret_ref,
            credentials=config.credentials,
        )
        return await self._upsert(
            channel=Channel.EMAIL.value,
            config={
                "ses_region": config.ses_region,
                "from_address": config.from_address,
            },
            secret_ref=secret_ref,
        )

    async def configure_sms(
        self,
        principal: AuthPrincipal | None,
        config: SmsChannelConfigInput,
    ) -> ChannelConfig:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        secret_ref = self._resolve_secret_ref(
            channel=Channel.SMS.value,
            secret_ref=config.secret_ref,
            credentials=config.credentials,
        )
        return await self._upsert(
            channel=Channel.SMS.value,
            config={"sns_region": config.sns_region},
            secret_ref=secret_ref,
        )

    async def configure_fcm(
        self,
        principal: AuthPrincipal | None,
        config: FcmChannelConfigInput,
    ) -> ChannelConfig:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        secret_ref = self._resolve_secret_ref(
            channel=Channel.PUSH_ANDROID.value,
            secret_ref=config.secret_ref,
            credentials=config.credentials,
        )
        return await self._upsert(
            channel=Channel.PUSH_ANDROID.value,
            config={"project_id": config.project_id},
            secret_ref=secret_ref,
        )

    async def configure_apns(
        self,
        principal: AuthPrincipal | None,
        config: ApnsChannelConfigInput,
    ) -> ChannelConfig:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        secret_ref = self._resolve_secret_ref(
            channel=Channel.PUSH_IOS.value,
            secret_ref=config.secret_ref,
            credentials=config.credentials,
        )
        return await self._upsert(
            channel=Channel.PUSH_IOS.value,
            config={
                "bundle_id": config.bundle_id,
                "team_id": config.team_id,
                "key_id": config.key_id,
                "environment": config.environment,
            },
            secret_ref=secret_ref,
        )

    async def get_config(self, principal: AuthPrincipal | None, channel: str) -> ChannelConfig:
        require_application_access(principal, self._application_id)
        record = await self._repository.get_by_channel(channel)
        if record is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Channel config not found")
        return record

    async def list_configs(self, principal: AuthPrincipal | None) -> list[ChannelConfig]:
        require_application_access(principal, self._application_id)
        return await self._repository.list_all()

    async def _upsert(
        self,
        *,
        channel: str,
        config: dict,
        secret_ref: str | None,
    ) -> ChannelConfig:
        existing = await self._repository.get_by_channel(channel)
        if existing is not None:
            existing.config = config
            existing.secret_ref = secret_ref
            existing.is_enabled = True
            return await self._repository.update(existing)

        record = ChannelConfig(
            application_id=_app_id(self._application_id),
            channel=channel,
            config=config,
            secret_ref=secret_ref,
            is_enabled=True,
        )
        return await self._repository.create(record)

    def _resolve_secret_ref(
        self,
        *,
        channel: str,
        secret_ref: str | None,
        credentials: str | None,
    ) -> str | None:
        if credentials is not None:
            ref = secret_ref or AwsSecretsService.build_secret_ref(
                application_id=self._application_id,
                channel=channel,
            )
            self._secrets.store_secret(ref, credentials)
            return ref
        return secret_ref

    @staticmethod
    def build(
        session: AsyncSession,
        application_id: str,
        secrets_service: AwsSecretsService | None = None,
    ) -> ChannelConfigService:
        return ChannelConfigService(session, application_id, secrets_service)
