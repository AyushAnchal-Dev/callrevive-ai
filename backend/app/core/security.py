"""
CallRevive AI — Security utilities.

Password hashing, JWT token management, and RBAC.
"""

from __future__ import annotations

import enum
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
# Passlib compatibility patch for bcrypt >= 4.1.0
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = About()

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


class Role(str, enum.Enum):
    """Application roles for RBAC."""

    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"


# ---------------------------------------------------------------------------
# JWT token schemas
# ---------------------------------------------------------------------------


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str  # user id
    role: str
    email: str
    business_id: str | None = None
    exp: datetime
    iat: datetime
    token_type: str  # "access" | "refresh"
    jti: str | None = None  # unique token id


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------


def create_access_token(
    user_id: UUID,
    role: str,
    email: str,
    business_id: UUID | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived JWT access token."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "business_id": str(business_id) if business_id else None,
        "exp": expires,
        "iat": now,
        "token_type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    role: str,
    email: str,
    business_id: UUID | None = None,
) -> str:
    """Create a long-lived JWT refresh token."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "business_id": str(business_id) if business_id else None,
        "exp": expires,
        "iat": now,
        "token_type": "refresh",
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# Token verification
# ---------------------------------------------------------------------------


def verify_token(token: str, *, expected_type: str = "access") -> TokenPayload:
    """
    Decode and verify a JWT token.

    Raises ``HTTPException(401)`` on invalid / expired tokens.
    """
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise credentials_exception

    token_type = payload.get("token_type")
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected '{expected_type}'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return TokenPayload(
            sub=payload["sub"],
            role=payload["role"],
            email=payload["email"],
            business_id=payload.get("business_id"),
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            token_type=token_type,
            jti=payload.get("jti"),
        )
    except (KeyError, ValueError):
        raise credentials_exception


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> TokenPayload:
    """FastAPI dependency — extract and verify the current user from the Bearer token."""
    return verify_token(credentials.credentials, expected_type="access")


class RoleChecker:
    """
    FastAPI dependency that enforces RBAC.

    Usage::

        @router.get("/admin-only", dependencies=[Depends(RoleChecker([Role.ADMIN]))])
        async def admin_endpoint(): ...
    """

    def __init__(self, allowed_roles: list[Role]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if user.role not in [r.value for r in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return user


# Convenience instances
require_admin = RoleChecker([Role.ADMIN])
require_manager = RoleChecker([Role.ADMIN, Role.MANAGER])
require_agent = RoleChecker([Role.ADMIN, Role.MANAGER, Role.AGENT])
