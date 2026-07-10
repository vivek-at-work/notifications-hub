from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.application_api_key import ApplicationApiKey


class ApplicationRepository:
    """Platform-level repository for Application tenants."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, application_id: str | uuid.UUID) -> Application | None:
        result = await self.session.execute(
            select(Application).where(Application.id == application_id),
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Application | None:
        result = await self.session.execute(select(Application).where(Application.slug == slug))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Application]:
        result = await self.session.execute(select(Application).order_by(Application.created_at))
        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        slug: str,
        retention_policy: dict[str, object] | None = None,
    ) -> Application:
        application = Application(
            name=name,
            slug=slug,
            retention_policy=retention_policy or {"notification_history_days": 90},
        )
        self.session.add(application)
        await self.session.flush()
        return application

    async def update(
        self,
        application: Application,
        *,
        name: str | None = None,
        retention_policy: dict[str, object] | None = None,
    ) -> Application:
        if name is not None:
            application.name = name
        if retention_policy is not None:
            application.retention_policy = retention_policy
        await self.session.flush()
        return application

    async def delete(self, application_id: str | uuid.UUID) -> bool:
        application = await self.get_by_id(application_id)
        if application is None:
            return False
        await self.session.delete(application)
        await self.session.flush()
        return True


class ApplicationApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        application_id: str | uuid.UUID,
        name: str,
        key_hash: str,
        scopes: list[str],
        key_prefix: str | None = None,
    ) -> ApplicationApiKey:
        record = ApplicationApiKey(
            application_id=application_id,
            name=name,
            key_prefix=key_prefix or key_hash[:8],
            key_hash=key_hash,
            scopes=scopes,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_by_application(
        self,
        application_id: str | uuid.UUID,
    ) -> list[ApplicationApiKey]:
        result = await self.session.execute(
            select(ApplicationApiKey)
            .where(ApplicationApiKey.application_id == application_id)
            .order_by(ApplicationApiKey.created_at.desc()),
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[ApplicationApiKey]:
        result = await self.session.execute(
            select(ApplicationApiKey).where(ApplicationApiKey.revoked_at.is_(None)),
        )
        return list(result.scalars().all())

    async def get_by_id(
        self,
        application_id: str | uuid.UUID,
        key_id: str | uuid.UUID,
    ) -> ApplicationApiKey | None:
        result = await self.session.execute(
            select(ApplicationApiKey).where(
                ApplicationApiKey.application_id == application_id,
                ApplicationApiKey.id == key_id,
            ),
        )
        return result.scalar_one_or_none()

    async def revoke(self, api_key: ApplicationApiKey) -> ApplicationApiKey:
        api_key.revoked_at = datetime.now(UTC)
        await self.session.flush()
        return api_key
