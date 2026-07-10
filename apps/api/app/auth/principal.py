from __future__ import annotations

from dataclasses import dataclass, field

from app.auth.roles import Role
from app.auth.scopes import Scope


@dataclass(frozen=True, slots=True)
class AuthPrincipal:
    role: Role
    application_id: str | None = None
    end_user_id: str | None = None
    user_id: str | None = None
    email: str | None = None
    scopes: frozenset[Scope] = field(default_factory=frozenset)
