from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import Request, Response


async def tracing_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """
    Bind a trace_id to structlog context for each HTTP request.
    """
    trace_id = request.headers.get("X-Trace-Id") or uuid4().hex

    with structlog.contextvars.bound_contextvars(trace_id=trace_id):
        return await call_next(request)
