from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_keys import generate_api_key, hash_api_key, verify_api_key
from app.auth.authorization import AuthorizationError, require_role, require_scope
from app.auth.oidc import OidcService, OidcSettings
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.auth.scopes import Scope
from app.repositories.application import ApplicationApiKeyRepository, ApplicationRepository
from app.services.application_service import ApplicationService


@pytest.mark.asyncio
async def test_api_key_generation_and_verification() -> None:
    plaintext = generate_api_key()
    assert plaintext.startswith("nh_")
    hashed = hash_api_key(plaintext)
    assert verify_api_key(plaintext, hashed)
    assert not verify_api_key("nh_wrong", hashed)


@pytest.mark.asyncio
async def test_oidc_issue_and_validate_token() -> None:
    oidc = OidcService(OidcSettings(jwt_secret="secret", audience="aud"))
    token = oidc.issue_token(
        role=Role.TENANT_ADMIN,
        subject="user-1",
        email="admin@example.com",
        application_id="00000000-0000-4000-8000-000000000001",
    )
    principal = oidc.validate_token(token)
    assert principal.role == Role.TENANT_ADMIN
    assert principal.application_id == "00000000-0000-4000-8000-000000000001"
    assert principal.email == "admin@example.com"


@pytest.mark.asyncio
async def test_require_role_denies_end_user() -> None:
    principal = AuthPrincipal(role=Role.END_USER, application_id="app-1", end_user_id="eu-1")
    with pytest.raises(AuthorizationError):
        require_role(principal, Role.TENANT_ADMIN)


@pytest.mark.asyncio
async def test_require_scope_for_client_app() -> None:
    principal = AuthPrincipal(
        role=Role.CLIENT_APP,
        application_id="app-1",
        scopes=frozenset({Scope.NOTIFICATIONS_READ}),
    )
    require_scope(principal, Scope.NOTIFICATIONS_READ)
    with pytest.raises(AuthorizationError):
        require_scope(principal, Scope.NOTIFICATIONS_SEND)


@pytest.mark.asyncio
async def test_application_service_crud_and_api_keys(db_session: AsyncSession) -> None:
    platform_admin = AuthPrincipal(role=Role.PLATFORM_ADMIN)
    service = ApplicationService(
        ApplicationRepository(db_session),
        ApplicationApiKeyRepository(db_session),
    )

    app_record = await service.create_application(
        platform_admin,
        name="Acme",
        slug="acme",
    )
    assert app_record.slug == "acme"

    tenant_admin = AuthPrincipal(role=Role.TENANT_ADMIN, application_id=str(app_record.id))
    key_result = await service.create_api_key(
        tenant_admin,
        str(app_record.id),
        name="integration",
        scopes=["notifications:send", "notifications:read"],
    )
    assert key_result.plaintext_key.startswith("nh_")
    assert verify_api_key(key_result.plaintext_key, key_result.api_key.key_hash)

    fetched = await service.get_application(tenant_admin, str(app_record.id))
    assert fetched.id == app_record.id
