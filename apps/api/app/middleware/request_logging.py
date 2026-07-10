from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging import log_http, reset_request_id, set_request_id

REQUEST_ID_HEADER = "x-request-id"
_HEALTH_PATHS = frozenset({"/health"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming_request_id or str(uuid.uuid4())
        token = set_request_id(request_id)

        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            reset_request_id(token)

        response.headers[REQUEST_ID_HEADER] = request_id

        if request.url.path not in _HEALTH_PATHS:
            duration_us = int((time.perf_counter() - start) * 1_000_000)
            client_ip = request.client.host if request.client else "unknown"
            log_http(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                client_ip=client_ip,
                duration_us=duration_us,
            )

        return response
