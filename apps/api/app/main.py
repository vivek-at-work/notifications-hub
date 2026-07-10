from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app
from strawberry.fastapi import GraphQLRouter

from app.config import get_settings
from app.db import create_tables, dispose_db, init_db
from app.graphql.context import GraphQLContext
from app.graphql.schema import schema
from app.logging import log_startup, setup_logging
from app.middleware.auth import AuthMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routes.health import router as health_router
from app.telemetry.otel import instrument_fastapi
from app.version import get_version


async def graphql_context(request: Request) -> AsyncIterator[GraphQLContext]:
    from app.db.session import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        yield GraphQLContext(request=request, session=session)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(log_level=settings.log_level, log_format=settings.resolved_log_format)
    log_startup(kind="app", action_name="startup", status="started")
    init_db(settings.database_url)
    await create_tables()
    instrument_fastapi(app)
    log_startup(kind="app", action_name="startup", status="completed")
    yield
    await dispose_db()
    log_startup(kind="app", action_name="shutdown", status="completed")


app = FastAPI(title="Notifications Hub API", version=get_version(), lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(health_router)
app.include_router(
    GraphQLRouter(schema, context_getter=graphql_context),
    prefix="/graphql",
)
app.mount("/metrics", make_asgi_app())
