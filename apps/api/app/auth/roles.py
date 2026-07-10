from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
    END_USER = "end_user"
    CLIENT_APP = "client_app"
