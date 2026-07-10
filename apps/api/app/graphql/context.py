from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from strawberry.fastapi import BaseContext

from app.auth.principal import AuthPrincipal
from app.services.application_service import ApplicationService
from app.services.channel_config_service import ChannelConfigService
from app.services.notification_category_service import NotificationCategoryService
from app.services.template_service import TemplateService


class GraphQLContext(BaseContext):
    def __init__(self, request: Request, session: AsyncSession) -> None:
        super().__init__()
        self.request = request
        self.session = session

    @property
    def principal(self) -> AuthPrincipal | None:
        return getattr(self.request.state, "principal", None)

    @property
    def application_id(self) -> str | None:
        principal = self.principal
        return principal.application_id if principal else None

    @property
    def application_service(self) -> ApplicationService:
        return ApplicationService.build(self.session)

    def channel_config_service(self) -> ChannelConfigService | None:
        if self.application_id is None:
            return None
        return ChannelConfigService.build(self.session, self.application_id)

    def notification_category_service(self) -> NotificationCategoryService | None:
        if self.application_id is None:
            return None
        return NotificationCategoryService.build(self.session, self.application_id)

    def template_service(self) -> TemplateService | None:
        return TemplateService.build(self.session)
