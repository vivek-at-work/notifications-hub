from __future__ import annotations

import pytest
from httpx import AsyncClient
from notifications_common.types import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.oidc import OidcService
from app.auth.principal import AuthPrincipal
from app.auth.roles import Role
from app.repositories.application import ApplicationRepository
from app.services.template_service import TemplateService


@pytest.mark.asyncio
async def test_template_graphql_queries(
    client: AsyncClient,
    db_session: AsyncSession,
    oidc_service: OidcService,
) -> None:
    app_repo = ApplicationRepository(db_session)
    app_record = await app_repo.create(name="GraphQL Tenant", slug="graphql-tenant")
    await db_session.commit()

    app_id = str(app_record.id)
    principal = AuthPrincipal(role=Role.TENANT_ADMIN, application_id=app_id)
    template_service = TemplateService.build(db_session)
    created = await template_service.create_version(
        principal,
        app_id,
        key="welcome",
        channel=Channel.EMAIL.value,
        subject="Welcome",
        body="Hello {{name}}",
        placeholders_schema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    )
    await db_session.commit()

    token = oidc_service.issue_token(
        role=Role.TENANT_ADMIN,
        subject="admin-1",
        email="admin@example.com",
        application_id=app_id,
    )
    headers = {"Authorization": f"Bearer {token}"}

    list_response = await client.post(
        "/graphql",
        headers=headers,
        json={
            "query": """
                query {
                  templates(page: 1, pageSize: 10) {
                    totalCount
                    edges { node { id key channel version } }
                  }
                }
            """
        },
    )
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert "errors" not in list_payload
    assert list_payload["data"]["templates"]["totalCount"] == 1
    assert list_payload["data"]["templates"]["edges"][0]["node"]["key"] == "welcome"

    detail_response = await client.post(
        "/graphql",
        headers=headers,
        json={
            "query": """
                query($id: ID!) {
                  template(id: $id) {
                    id
                    key
                    body
                  }
                }
            """,
            "variables": {"id": str(created.id)},
        },
    )
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["data"]["template"]["body"] == "Hello {{name}}"


@pytest.mark.asyncio
async def test_template_graphql_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/graphql",
        json={"query": "{ templates { totalCount } }"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("errors")
    assert "PERMISSION_DENIED" in payload["errors"][0]["message"]
