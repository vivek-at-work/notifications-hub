from __future__ import annotations

from notifications_common.errors import ErrorCode, PlatformError

from app.auth.audit import log_permission_denied
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.auth.scopes import Scope


class AuthorizationError(PlatformError):
    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(ErrorCode.PERMISSION_DENIED, message, field=field)


def require_authenticated(principal: AuthPrincipal | None) -> AuthPrincipal:
    if principal is None:
        raise AuthorizationError("Authentication required")
    return principal


def require_role(principal: AuthPrincipal | None, *roles: Role) -> AuthPrincipal:
    auth = require_authenticated(principal)
    if auth.role not in roles:
        log_permission_denied(
            reason="insufficient_role",
            required_roles=[role.value for role in roles],
            actual_role=auth.role.value,
            application_id=auth.application_id,
        )
        raise AuthorizationError("Insufficient role for this operation")
    return auth


def require_scope(principal: AuthPrincipal | None, scope: Scope) -> AuthPrincipal:
    auth = require_authenticated(principal)
    if auth.role != Role.CLIENT_APP:
        return auth
    if scope not in auth.scopes:
        log_permission_denied(
            reason="insufficient_scope",
            required_scope=scope.value,
            application_id=auth.application_id,
        )
        raise AuthorizationError(f"Missing required scope: {scope.value}")
    return auth


def require_application_access(
    principal: AuthPrincipal | None,
    application_id: str,
) -> AuthPrincipal:
    auth = require_authenticated(principal)
    if auth.role == Role.PLATFORM_ADMIN:
        return auth
    if auth.role == Role.TENANT_ADMIN and auth.application_id == application_id:
        return auth
    if auth.role == Role.CLIENT_APP and auth.application_id == application_id:
        return auth
    log_permission_denied(
        reason="cross_tenant_access",
        requested_application_id=application_id,
        principal_application_id=auth.application_id,
        role=auth.role.value,
    )
    raise AuthorizationError("Access denied for this application")
