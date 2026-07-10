from __future__ import annotations

import contextvars

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id",
    default=None,
)


def get_request_id() -> str | None:
    return request_id_var.get()


def set_request_id(request_id: str) -> contextvars.Token[str | None]:
    return request_id_var.set(request_id)


def reset_request_id(token: contextvars.Token[str | None]) -> None:
    request_id_var.reset(token)
