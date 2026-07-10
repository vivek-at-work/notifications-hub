from __future__ import annotations

import uuid
from dataclasses import dataclass

from notifications_common.errors import ErrorCode, PlatformError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_keys import generate_api_key, hash_api_key
from app.auth.authorization import require_role
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.models.application import Application
from app.models.application_api_key import ApplicationApiKey
from app.repositories.application import ApplicationApiKeyRepository, ApplicationRepository


@dataclass(frozen=True, slots=True)
class ApiKeyCreateResult:
    api_key: ApplicationApiKey
    plaintext_key: str


def _parse_application_id(application_id: str) -> uuid.UUID:
    return uuid.UUID(application_id)


class ApplicationService:
    def __init__(
        self,
        repository: ApplicationRepository,
        api_key_repository: ApplicationApiKeyRepository,
    ) -> None:
        self._repository = repository
        self._api_key_repository = api_key_repository

    async def create_application(
        self,
        principal: AuthPrincipal | None,
        *,
        name: str,
        slug: str,
        retention_policy: dict | None = None,
    ) -> Application:
        require_role(principal, Role.PLATFORM_ADMIN)
        existing = await self._repository.get_by_slug(slug)
        if existing is not None:
            raise PlatformError(ErrorCode.CONFLICT, f"Application slug already exists: {slug}")
        return await self._repository.create(
            name=name,
            slug=slug,
            retention_policy=retention_policy,
        )

    async def get_application(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
    ) -> Application:
        from app.auth.authorization import require_application_access

        require_application_access(principal, application_id)
        app = await self._repository.get_by_id(_parse_application_id(application_id))
        if app is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Application not found")
        return app

    async def get_by_slug(self, slug: str) -> Application | None:
        return await self._repository.get_by_slug(slug)

    async def list_applications(self, principal: AuthPrincipal | None) -> list[Application]:
        require_role(principal, Role.PLATFORM_ADMIN)
        return await self._repository.list_all()

    async def update_application(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        *,
        name: str | None = None,
        retention_policy: dict | None = None,
    ) -> Application:
        from app.auth.authorization import require_application_access

        require_application_access(principal, application_id)
        app = await self._repository.get_by_id(_parse_application_id(application_id))
        if app is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Application not found")
        if name is not None:
            app.name = name
        if retention_policy is not None:
            app.retention_policy = retention_policy
        return await self._repository.update(app)

    async def delete_application(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
    ) -> None:
        require_role(principal, Role.PLATFORM_ADMIN)
        app = await self._repository.get_by_id(_parse_application_id(application_id))
        if app is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Application not found")
        await self._repository.delete(app)

    async def create_api_key(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        *,
        name: str,
        scopes: list[str],
    ) -> ApiKeyCreateResult:
        from app.auth.authorization import require_application_access

        app_uuid = _parse_application_id(application_id)
        require_application_access(principal, application_id)
        plaintext = generate_api_key()
        record = await self._api_key_repository.create(
            application_id=app_uuid,
            name=name,
            key_prefix=plaintext[:16],
            key_hash=hash_api_key(plaintext),
            scopes=scopes,
        )
        return ApiKeyCreateResult(api_key=record, plaintext_key=plaintext)

    async def revoke_api_key(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        key_id: str,
    ) -> ApplicationApiKey:
        from app.auth.authorization import require_application_access

        require_application_access(principal, application_id)
        record = await self._api_key_repository.get_by_id(
            _parse_application_id(application_id),
            uuid.UUID(key_id),
        )
        if record is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "API key not found")
        return await self._api_key_repository.revoke(record)

    @staticmethod
    def build(session: AsyncSession) -> ApplicationService:
        return ApplicationService(
            ApplicationRepository(session),
            ApplicationApiKeyRepository(session),
        )
