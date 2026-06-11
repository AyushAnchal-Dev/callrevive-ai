"""
CallRevive AI — Custom exceptions and FastAPI exception handlers.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse


# ---------------------------------------------------------------------------
# Base exception
# ---------------------------------------------------------------------------


class AppException(Exception):
    """Base application exception.

    All custom exceptions inherit from this so they can be caught by a single
    handler.
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(message)


# ---------------------------------------------------------------------------
# Concrete exceptions
# ---------------------------------------------------------------------------


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        detail = {}
        if resource:
            detail["resource"] = resource
        if resource_id:
            detail["resource_id"] = resource_id
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or None,
        )


class UnauthorizedException(AppException):
    """Authentication failure (401)."""

    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationException(AppException):
    """Business-logic validation error (422)."""

    def __init__(self, message: str = "Validation error", errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors} if errors else None,
        )


class ConflictException(AppException):
    """Conflict — e.g. duplicate resource (409)."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class ExternalServiceException(AppException):
    """An external service (Twilio, Gemini, etc.) returned an error."""

    def __init__(
        self,
        service: str,
        message: str = "External service error",
        original_error: str | None = None,
    ) -> None:
        detail = {"service": service}
        if original_error:
            detail["original_error"] = original_error
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class RateLimitException(AppException):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------


async def app_exception_handler(request: Request, exc: AppException) -> ORJSONResponse:
    """Handle all AppException subclasses."""
    body: dict[str, Any] = {
        "success": False,
        "message": exc.message,
    }
    if exc.detail:
        body["detail"] = exc.detail

    return ORJSONResponse(
        status_code=exc.status_code,
        content=body,
        headers=exc.headers,
    )


async def _generic_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    """Catch-all for unhandled exceptions — never leak stack traces."""
    import logging
    import traceback

    logger = logging.getLogger("callrevive.exceptions")
    logger.error(
        "Unhandled exception on %s %s: %s\n%s",
        request.method,
        request.url.path,
        str(exc),
        traceback.format_exc(),
    )

    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _generic_exception_handler)
