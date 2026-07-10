from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from notifications_common.errors import ErrorCode, PlatformError

from app.auth.principal import AuthPrincipal
from app.auth.roles import Role


@dataclass(frozen=True, slots=True)
class OidcSettings:
    issuer: str = "https://accounts.google.com"
    audience: str = "notifications-hub-test"
    jwt_secret: str = "test-oidc-secret"
    jwt_algorithm: str = "HS256"
    token_ttl_seconds: int = 3600


class OidcService:
    """Google OIDC JWT issuance stub — configurable and testable without real Google."""

    def __init__(self, settings: OidcSettings | None = None) -> None:
        self._settings = settings or OidcSettings()

    def issue_token(
        self,
        *,
        role: Role,
        subject: str,
        email: str,
        application_id: str | None = None,
        end_user_id: str | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "sub": subject,
            "email": email,
            "role": role.value,
            "iat": now,
            "exp": now + timedelta(seconds=self._settings.token_ttl_seconds),
        }
        if application_id is not None:
            payload["application_id"] = application_id
        if end_user_id is not None:
            payload["end_user_id"] = end_user_id
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    def validate_token(self, token: str) -> AuthPrincipal:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
                audience=self._settings.audience,
                options={"require": ["exp", "sub", "role"]},
            )
        except jwt.PyJWTError as exc:
            raise PlatformError(ErrorCode.PERMISSION_DENIED, "Invalid or expired token") from exc

        role = Role(payload["role"])
        return AuthPrincipal(
            role=role,
            application_id=payload.get("application_id"),
            end_user_id=payload.get("end_user_id"),
            user_id=str(payload["sub"]),
            email=payload.get("email"),
        )

    def exchange_google_id_token(self, google_id_token: str) -> AuthPrincipal:
        """Stub exchange — in production this validates Google ID token via JWKS."""
        if not google_id_token:
            raise PlatformError(ErrorCode.PERMISSION_DENIED, "Missing Google ID token")
        return self.validate_token(google_id_token)
