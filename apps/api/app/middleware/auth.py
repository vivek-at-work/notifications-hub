from __future__ import annotations

from collections.abc import Awaitable, Callable

from notifications_common.errors import ErrorCode, PlatformError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.auth.api_keys import is_api_key_token, verify_api_key
from app.auth.audit import log_authentication_failure
from app.auth.oidc import OidcService
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.auth.scopes import parse_scopes
from app.repositories.application import ApplicationApiKeyRepository


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        session_factory: Callable[[], AsyncSession] | None = None,
        oidc_service: OidcService | None = None,
    ) -> None:
        super().__init__(app)
        self._session_factory = session_factory
        self._oidc = oidc_service or OidcService()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.removeprefix("Bearer ").strip() if auth_header else ""

        if not token:
            request.state.principal = None
            request.state.application_id = None
            request.state.scopes = frozenset()
            return await call_next(request)

        try:
            principal = await self._authenticate(token)
        except PlatformError as exc:
            log_authentication_failure(reason=exc.code.value, message=exc.message)
            return JSONResponse(
                status_code=401,
                content={"code": exc.code.value, "message": exc.message},
            )

        request.state.principal = principal
        request.state.application_id = principal.application_id
        request.state.scopes = principal.scopes
        return await call_next(request)

    async def _authenticate(self, token: str) -> AuthPrincipal:
        if is_api_key_token(token):
            return await self._authenticate_api_key(token)
        return self._oidc.validate_token(token)

    async def _authenticate_api_key(self, token: str) -> AuthPrincipal:
        from app.db.session import get_session_factory

        factory = self._session_factory or get_session_factory()
        async with factory() as session:
            repo = ApplicationApiKeyRepository(session)
            keys = await repo.list_active()
            for record in keys:
                if record.revoked_at is not None:
                    continue
                if verify_api_key(token, record.key_hash):
                    return AuthPrincipal(
                        role=Role.CLIENT_APP,
                        application_id=str(record.application_id),
                        scopes=parse_scopes(record.scopes),
                    )
        raise PlatformError(
            ErrorCode.PERMISSION_DENIED,
            "Invalid or revoked API key",
        )
