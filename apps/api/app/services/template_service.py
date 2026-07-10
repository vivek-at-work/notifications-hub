from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from notifications_common.errors import ErrorCode, PlatformError
from notifications_common.placeholders import PlaceholderRenderer, validate_placeholders
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authorization import require_application_access, require_role
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.models.template import Template
from app.repositories.template import TemplateRepository


@dataclass(frozen=True, slots=True)
class RenderedTemplate:
    subject: str | None
    body: str


class TemplateService:
    def __init__(
        self,
        session: AsyncSession,
        renderer: PlaceholderRenderer | None = None,
    ) -> None:
        self._session = session
        self._renderer = renderer or PlaceholderRenderer()

    def _repository(self, application_id: str) -> TemplateRepository:
        return TemplateRepository(self._session, application_id)

    async def create_version(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        *,
        key: str,
        channel: str,
        subject: str | None,
        body: str,
        placeholders_schema: dict[str, Any],
    ) -> Template:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, application_id)
        return await self._repository(application_id).create_version(
            key=key,
            channel=channel,
            subject=subject,
            body=body,
            placeholders_schema=placeholders_schema,
        )

    async def activate_version(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        template_id: str,
    ) -> Template:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, application_id)
        template = await self._repository(application_id).activate(template_id)
        if template is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Template not found")
        return template

    async def get_template(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        template_id: str,
    ) -> Template:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, application_id)
        template = await self._repository(application_id).get_by_id(template_id)
        if template is None:
            raise PlatformError(ErrorCode.NOT_FOUND, "Template not found")
        return template

    async def get_active_template(
        self,
        application_id: str,
        key: str,
        channel: str,
    ) -> Template:
        template = await self._repository(application_id).get_active(key, channel)
        if template is None:
            raise PlatformError(
                ErrorCode.TEMPLATE_NOT_FOUND,
                f"No active template for key={key} channel={channel}",
            )
        return template

    async def list_templates(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        *,
        channel: str | None = None,
        key: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Template], int]:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, application_id)
        if page < 1:
            raise PlatformError(ErrorCode.VALIDATION_ERROR, "page must be >= 1", field="page")
        if page_size < 1 or page_size > 100:
            raise PlatformError(
                ErrorCode.VALIDATION_ERROR,
                "page_size must be between 1 and 100",
                field="pageSize",
            )
        offset = (page - 1) * page_size
        return await self._repository(application_id).list_active(
            channel=channel,
            key=key,
            offset=offset,
            limit=page_size,
        )

    async def list_versions(
        self,
        principal: AuthPrincipal | None,
        application_id: str,
        key: str,
        channel: str,
    ) -> list[Template]:
        require_role(principal, Role.TENANT_ADMIN, Role.PLATFORM_ADMIN)
        require_application_access(principal, application_id)
        return await self._repository(application_id).list_versions(key, channel)

    def validate_placeholders(self, template: Template, values: dict[str, Any]) -> None:
        validate_placeholders(template.placeholders_schema, values)

    def render(
        self,
        template: Template,
        values: dict[str, Any],
    ) -> RenderedTemplate:
        self.validate_placeholders(template, values)
        string_values = {key: str(value) for key, value in values.items()}
        subject = (
            self._renderer.render(template.subject, string_values) if template.subject else None
        )
        body = self._renderer.render(template.body, string_values)
        return RenderedTemplate(subject=subject, body=body)

    @staticmethod
    def build(session: AsyncSession) -> TemplateService:
        return TemplateService(session)
