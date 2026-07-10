from __future__ import annotations

import uuid

from notifications_common.errors import ErrorCode, PlatformError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authorization import require_application_access, require_role
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.models.preference import NotificationCategory
from app.repositories.notification_category import NotificationCategoryRepository


def _app_id(application_id: str) -> uuid.UUID:
    return uuid.UUID(application_id)


class NotificationCategoryService:
    def __init__(self, session: AsyncSession, application_id: str) -> None:
        self._application_id = application_id
        self._repository = NotificationCategoryRepository(session, _app_id(application_id))

    async def create_category(
        self,
        principal: AuthPrincipal | None,
        *,
        key: str,
        name: str,
        is_mandatory: bool = False,
    ) -> NotificationCategory:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        existing = await self._repository.get_by_key(key)
        if existing is not None:
            raise PlatformError(ErrorCode.CONFLICT, f"Category key already exists: {key}")
        return await self._repository.create(key=key, name=name, is_mandatory=is_mandatory)

    async def get_category(
        self,
        principal: AuthPrincipal | None,
        category_id: str,
    ) -> NotificationCategory:
        require_application_access(principal, self._application_id)
        category = await self._repository.get_by_id(uuid.UUID(category_id))
        if category is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Notification category not found")
        return category

    async def list_categories(self, principal: AuthPrincipal | None) -> list[NotificationCategory]:
        require_application_access(principal, self._application_id)
        return await self._repository.list_all()

    async def update_category(
        self,
        principal: AuthPrincipal | None,
        category_id: str,
        *,
        name: str | None = None,
        is_mandatory: bool | None = None,
    ) -> NotificationCategory:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        category = await self._repository.get_by_id(uuid.UUID(category_id))
        if category is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Notification category not found")
        if name is not None:
            category.name = name
        if is_mandatory is not None:
            category.is_mandatory = is_mandatory
        return await self._repository.update(category, name=name, is_mandatory=is_mandatory)

    async def delete_category(self, principal: AuthPrincipal | None, category_id: str) -> None:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, self._application_id)
        deleted = await self._repository.delete(uuid.UUID(category_id))
        if not deleted:
            raise PlatformError(ErrorCode.NOT_FOUND, "Notification category not found")

    @staticmethod
    def build(session: AsyncSession, application_id: str) -> NotificationCategoryService:
        return NotificationCategoryService(session, application_id)
