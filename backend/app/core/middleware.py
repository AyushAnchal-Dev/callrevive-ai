"""
CallRevive AI — Middleware stack.

Request-ID injection, audit logging, CORS setup, and rate limiting.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings

logger = logging.getLogger("callrevive.middleware")

# ---------------------------------------------------------------------------
# Rate Limiter (global singleton)
# ---------------------------------------------------------------------------

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    storage_uri=get_settings().REDIS_URL if get_settings().REDIS_URL else "memory://",
)


# ---------------------------------------------------------------------------
# Request ID Middleware
# ---------------------------------------------------------------------------


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique ``X-Request-ID`` header into every request/response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Store on request state so downstream handlers can access it
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ---------------------------------------------------------------------------
# Audit / Access Logging Middleware
# ---------------------------------------------------------------------------


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log every request with timing, status code, and request ID."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000
        request_id = getattr(request.state, "request_id", "N/A")

        logger.info(
            "method=%s path=%s status=%d duration_ms=%.2f request_id=%s client=%s",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
            request_id,
            request.client.host if request.client else "unknown",
        )

        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
        return response


# ---------------------------------------------------------------------------
# CORS Setup
# ---------------------------------------------------------------------------


def setup_cors(app: FastAPI) -> None:
    """Attach CORS middleware to the application."""
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
    )


# ---------------------------------------------------------------------------
# Rate Limiting Setup
# ---------------------------------------------------------------------------


def setup_rate_limiting(app: FastAPI) -> None:
    """Attach the SlowAPI rate limiter to the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ---------------------------------------------------------------------------
# Register All Middleware
# ---------------------------------------------------------------------------


def register_middleware(app: FastAPI) -> None:
    """Register the full middleware stack in the correct order.

    Middleware is executed in reverse registration order (last added = first
    executed), so we register in bottom-up priority:
      1. CORS (outermost — must be first to execute)
      2. Request ID
      3. Audit logging (innermost — logs after response is built)
    """
    # 3. Audit logging — innermost
    app.add_middleware(AuditLogMiddleware)

    # 2. Request ID — second
    app.add_middleware(RequestIDMiddleware)

    # 1. CORS — outermost (registered last so it executes first)
    setup_cors(app)

    # Rate limiting
    setup_rate_limiting(app)
