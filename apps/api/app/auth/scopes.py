from __future__ import annotations

from enum import StrEnum


class Scope(StrEnum):
    NOTIFICATIONS_SEND = "notifications:send"
    NOTIFICATIONS_READ = "notifications:read"
    DEVICES_REGISTER = "devices:register"
    USERS_LINK = "users:link"


ALL_SCOPES = frozenset(Scope)


def parse_scopes(raw: list[str]) -> frozenset[Scope]:
    return frozenset(Scope(value) for value in raw if value in Scope._value2member_map_)


def scope_values(scopes: frozenset[Scope]) -> list[str]:
    return sorted(scope.value for scope in scopes)
