from __future__ import annotations

import uuid

from app.models.preference import NotificationCategory
from app.repositories.base import TenantScopedRepository


class NotificationCategoryRepository(TenantScopedRepository[NotificationCategory]):
    model = NotificationCategory

    async def create(
        self,
        *,
        key: str,
        name: str,
        is_mandatory: bool = False,
    ) -> NotificationCategory:
        record = NotificationCategory(
            application_id=self.application_id,
            key=key,
            name=name,
            is_mandatory=is_mandatory,
        )
        return await self.add(record)

    async def get_by_id(self, category_id: str | uuid.UUID) -> NotificationCategory | None:
        result = await self.session.execute(
            self._scoped_select().where(NotificationCategory.id == category_id),
        )
        return result.scalar_one_or_none()

    async def get_by_key(self, key: str) -> NotificationCategory | None:
        result = await self.session.execute(
            self._scoped_select().where(NotificationCategory.key == key),
        )
        return result.scalar_one_or_none()

    async def list_by_application(self) -> list[NotificationCategory]:
        result = await self.session.execute(
            self._scoped_select().order_by(NotificationCategory.key),
        )
        return list(result.scalars().all())

    async def update(
        self,
        category: NotificationCategory,
        *,
        name: str | None = None,
        is_mandatory: bool | None = None,
    ) -> NotificationCategory:
        if category.application_id != self.application_id:
            raise ValueError("NotificationCategory application_id must match repository scope")
        if name is not None:
            category.name = name
        if is_mandatory is not None:
            category.is_mandatory = is_mandatory
        await self.session.flush()
        return category

    async def delete(self, category_id: str | uuid.UUID) -> bool:
        category = await self.get_by_id(category_id)
        if category is None:
            return False
        await self.session.delete(category)
        await self.session.flush()
        return True
