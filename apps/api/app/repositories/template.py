from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template
from app.repositories.base import TenantScopedRepository


class TemplateRepository(TenantScopedRepository[Template]):
    model = Template

    def __init__(self, session: AsyncSession, application_id: str | uuid.UUID) -> None:
        app_uuid = uuid.UUID(str(application_id))
        super().__init__(session, app_uuid)

    async def create_version(
        self,
        *,
        key: str,
        channel: str,
        subject: str | None,
        body: str,
        placeholders_schema: dict[str, Any],
    ) -> Template:
        max_version_result = await self.session.execute(
            select(func.coalesce(func.max(Template.version), 0)).where(
                Template.application_id == self.application_id,
                Template.key == key,
                Template.channel == channel,
            ),
        )
        next_version = int(max_version_result.scalar_one()) + 1

        await self.session.execute(
            update(Template)
            .where(
                Template.application_id == self.application_id,
                Template.key == key,
                Template.channel == channel,
                Template.is_active.is_(True),
            )
            .values(is_active=False),
        )

        record = Template(
            application_id=self.application_id,
            key=key,
            channel=channel,
            version=next_version,
            subject=subject,
            body=body,
            placeholders_schema=placeholders_schema,
            is_active=True,
        )
        return await self.add(record)

    async def get_by_id(self, template_id: str | uuid.UUID) -> Template | None:
        resolved_id = (
            template_id if isinstance(template_id, uuid.UUID) else uuid.UUID(str(template_id))
        )
        result = await self.session.execute(
            self._scoped_select().where(Template.id == resolved_id),
        )
        return result.scalar_one_or_none()

    async def get_active(self, key: str, channel: str) -> Template | None:
        result = await self.session.execute(
            self._scoped_select().where(
                Template.key == key,
                Template.channel == channel,
                Template.is_active.is_(True),
            ),
        )
        return result.scalar_one_or_none()

    async def get_by_key_and_channel(
        self,
        key: str,
        channel: str,
        *,
        active_only: bool = True,
    ) -> Template | None:
        stmt = (
            self._scoped_select()
            .where(Template.key == key, Template.channel == channel)
            .order_by(Template.version.desc())
        )
        if active_only:
            stmt = stmt.where(Template.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_active(
        self,
        *,
        channel: str | None = None,
        key: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Template], int]:
        query = self._scoped_select().where(Template.is_active.is_(True))
        count_query = (
            select(func.count())
            .select_from(Template)
            .where(
                Template.application_id == self.application_id,
                Template.is_active.is_(True),
            )
        )

        if channel is not None:
            query = query.where(Template.channel == channel)
            count_query = count_query.where(Template.channel == channel)
        if key is not None:
            query = query.where(Template.key == key)
            count_query = count_query.where(Template.key == key)

        total_result = await self.session.execute(count_query)
        total = int(total_result.scalar_one())

        result = await self.session.execute(
            query.order_by(Template.key, Template.channel).offset(offset).limit(limit),
        )
        return list(result.scalars().all()), total

    async def list_by_channel(self, channel: str) -> list[Template]:
        result = await self.session.execute(
            self._scoped_select()
            .where(Template.channel == channel)
            .order_by(Template.key, Template.version.desc()),
        )
        return list(result.scalars().all())

    async def list_versions(self, key: str, channel: str) -> list[Template]:
        result = await self.session.execute(
            self._scoped_select()
            .where(Template.key == key, Template.channel == channel)
            .order_by(Template.version.desc()),
        )
        return list(result.scalars().all())

    async def activate(self, template_id: str) -> Template | None:
        target = await self.get_by_id(template_id)
        if target is None:
            return None

        await self.session.execute(
            update(Template)
            .where(
                Template.application_id == self.application_id,
                Template.key == target.key,
                Template.channel == target.channel,
                Template.is_active.is_(True),
            )
            .values(is_active=False),
        )
        target.is_active = True
        await self.session.flush()
        return target

    async def create(self, template: Template) -> Template:
        return await self.add(template)
