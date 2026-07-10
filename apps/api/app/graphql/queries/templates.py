from __future__ import annotations

from typing import TYPE_CHECKING

import strawberry

from app.graphql.types.pagination import PageInfo
from app.graphql.types.template import (
    TemplateConnection,
    TemplateEdge,
    TemplateType,
    TemplateWhereInput,
    _platform_error_to_graphql,
)

if TYPE_CHECKING:
    from app.graphql.context import GraphQLContext


@strawberry.type
class TemplateQuery:
    @strawberry.field(description="List active templates for the tenant admin's application")
    async def templates(
        self,
        info: strawberry.Info[GraphQLContext, None],
        where: TemplateWhereInput | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TemplateConnection:
        ctx = info.context
        principal = ctx.principal
        service = ctx.template_service()
        application_id = ctx.application_id
        if principal is None or service is None or application_id is None:
            raise ValueError("PERMISSION_DENIED: Authentication required")

        channel = where.channel.eq if where and where.channel else None
        key = where.key.eq if where and where.key else None

        try:
            records, total = await service.list_templates(
                principal,
                application_id,
                channel=channel,
                key=key,
                page=page,
                page_size=page_size,
            )
        except Exception as exc:
            raise _platform_error_to_graphql(exc) from exc

        edges = [TemplateEdge(node=TemplateType.from_model(record)) for record in records]
        return TemplateConnection(
            edges=edges,
            total_count=total,
            page_info=PageInfo(
                page=page,
                page_size=page_size,
                total_count=total,
                has_next_page=(page * page_size) < total,
                has_previous_page=page > 1,
            ),
        )

    @strawberry.field(description="Get a template by ID for tenant admin")
    async def template(
        self,
        info: strawberry.Info[GraphQLContext, None],
        id: strawberry.ID,
    ) -> TemplateType | None:
        ctx = info.context
        principal = ctx.principal
        service = ctx.template_service()
        application_id = ctx.application_id
        if principal is None or service is None or application_id is None:
            raise ValueError("PERMISSION_DENIED: Authentication required")

        try:
            record = await service.get_template(principal, application_id, str(id))
        except Exception as exc:
            from notifications_common.errors import ErrorCode, PlatformError

            if isinstance(exc, PlatformError) and exc.code == ErrorCode.NOT_FOUND:
                return None
            raise _platform_error_to_graphql(exc) from exc

        return TemplateType.from_model(record)
