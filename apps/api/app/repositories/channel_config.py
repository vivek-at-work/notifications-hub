from __future__ import annotations

from typing import Any

from app.models.channel_config import ChannelConfig
from app.repositories.base import TenantScopedRepository


class ChannelConfigRepository(TenantScopedRepository[ChannelConfig]):
    model = ChannelConfig

    async def upsert(
        self,
        *,
        channel: str,
        config: dict[str, Any],
        secret_ref: str | None,
    ) -> ChannelConfig:
        existing = await self.get_by_channel(channel)
        if existing is not None:
            existing.config = config
            existing.secret_ref = secret_ref
            await self.session.flush()
            return existing

        record = ChannelConfig(
            application_id=self.application_id,
            channel=channel,
            config=config,
            secret_ref=secret_ref,
        )
        return await self.add(record)

    async def get_by_channel(self, channel: str) -> ChannelConfig | None:
        result = await self.session.execute(
            self._scoped_select().where(ChannelConfig.channel == channel),
        )
        return result.scalar_one_or_none()

    async def list_by_application(self) -> list[ChannelConfig]:
        result = await self.session.execute(
            self._scoped_select().order_by(ChannelConfig.channel),
        )
        return list(result.scalars().all())

    async def list_enabled(self) -> list[ChannelConfig]:
        result = await self.session.execute(
            self._scoped_select().where(ChannelConfig.is_enabled.is_(True)),
        )
        return list(result.scalars().all())

    async def create(self, channel_config: ChannelConfig) -> ChannelConfig:
        return await self.add(channel_config)

    async def update(self, channel_config: ChannelConfig) -> ChannelConfig:
        if channel_config.application_id != self.application_id:
            raise ValueError("ChannelConfig application_id must match repository scope")
        self.session.add(channel_config)
        await self.session.flush()
        return channel_config

    async def delete(self, channel: str) -> bool:
        record = await self.get_by_channel(channel)
        if record is None:
            return False
        await self.session.delete(record)
        await self.session.flush()
        return True
