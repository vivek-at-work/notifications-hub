from __future__ import annotations

import strawberry

from app.graphql.queries.templates import TemplateQuery
from app.version import get_version


@strawberry.type
class Query(TemplateQuery):
    @strawberry.field(description="Simple health probe over GraphQL")
    def health(self) -> str:
        return "healthy"

    @strawberry.field(description="Application semantic version")
    def version(self) -> str:
        return get_version()


@strawberry.type
class Mutation:
    @strawberry.field(description="Echo a message — minimal mutation contract")
    def echo(self, message: str) -> str:
        return message


schema = strawberry.Schema(query=Query, mutation=Mutation)
