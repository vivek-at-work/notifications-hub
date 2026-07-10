from __future__ import annotations

import uuid
from typing import TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class TenantScopedRepository[ModelT: DeclarativeBase]:
    """Base repository that enforces application_id scoping on every query."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession, application_id: str | uuid.UUID) -> None:
        self.session = session
        self.application_id = (
            application_id
            if isinstance(application_id, uuid.UUID)
            else uuid.UUID(str(application_id))
        )

    def _scoped_select(self) -> Select[tuple[ModelT]]:
        return select(self.model).where(self.model.application_id == self.application_id)  # type: ignore[attr-defined]

    async def get_by_id(self, entity_id: str | uuid.UUID) -> ModelT | None:
        resolved_id = entity_id if isinstance(entity_id, uuid.UUID) else uuid.UUID(str(entity_id))
        stmt = self._scoped_select().where(self.model.id == resolved_id)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelT]:
        result = await self.session.execute(self._scoped_select())
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        if getattr(entity, "application_id", None) != self.application_id:
            raise ValueError(
                f"Entity application_id must match repository scope ({self.application_id})"
            )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: ModelT) -> None:
        if getattr(entity, "application_id", None) != self.application_id:
            raise ValueError(
                f"Entity application_id must match repository scope ({self.application_id})"
            )
        await self.session.delete(entity)
        await self.session.flush()
