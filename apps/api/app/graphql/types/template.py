from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import strawberry

from app.graphql.types.pagination import PageInfo
from app.models.template import Template

if TYPE_CHECKING:
    pass


@strawberry.type
class TemplateType:
    id: strawberry.ID
    application_id: strawberry.ID
    key: str
    channel: str
    version: int
    subject: str | None
    body: str
    placeholders_schema: strawberry.scalars.JSON
    is_active: bool
    created_at: datetime

    @classmethod
    def from_model(cls, template: Template) -> TemplateType:
        return cls(
            id=strawberry.ID(str(template.id)),
            application_id=strawberry.ID(str(template.application_id)),
            key=template.key,
            channel=template.channel,
            version=template.version,
            subject=template.subject,
            body=template.body,
            placeholders_schema=template.placeholders_schema,
            is_active=template.is_active,
            created_at=template.created_at,
        )


@strawberry.type
class TemplateEdge:
    node: TemplateType


@strawberry.type
class TemplateConnection:
    edges: list[TemplateEdge]
    total_count: int
    page_info: PageInfo


@strawberry.input
class TemplateChannelFilter:
    eq: str | None = None


@strawberry.input
class TemplateKeyFilter:
    eq: str | None = None


@strawberry.input
class TemplateWhereInput:
    channel: TemplateChannelFilter | None = None
    key: TemplateKeyFilter | None = None


def _platform_error_to_graphql(exc: Exception) -> Exception:
    from notifications_common.errors import PlatformError

    if isinstance(exc, PlatformError):
        return ValueError(f"{exc.code.value}: {exc.message}")
    return exc
