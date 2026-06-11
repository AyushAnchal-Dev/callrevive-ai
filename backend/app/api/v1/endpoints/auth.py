"""CallRevive AI — Authentication endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DBSession):
    """Register a new user account."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role="admin",
        phone_number=data.phone_number,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    from app.models.business import Business
    if data.businessName:
        business = Business(
            name=data.businessName,
            category=data.businessCategory or "Other",
            phone_number=data.phone_number or "",
            email=data.email,
            owner_id=user.id,
        )
        db.add(business)
        await db.flush()
        user.business_id = business.id

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user_id=user.id, role=user.role, email=user.email, business_id=user.business_id)
    refresh_token = create_refresh_token(user_id=user.id, role=user.role, email=user.email, business_id=user.business_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DBSession):
    """Authenticate user and return JWT tokens."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token(user_id=user.id, role=user.role, email=user.email, business_id=user.business_id)
    refresh_token = create_refresh_token(user_id=user.id, role=user.role, email=user.email, business_id=user.business_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: DBSession):
    """Refresh access token using a valid refresh token."""
    payload = verify_token(data.refresh_token, expected_type="refresh")

    import uuid

    user_id = payload.sub
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(user_id=user.id, role=user.role, email=user.email, business_id=user.business_id)
    new_refresh = create_refresh_token(user_id=user.id, role=user.role, email=user.email, business_id=user.business_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        token_type="bearer",
    )


@router.post("/forgot-password", status_code=200)
async def forgot_password(data: ForgotPasswordRequest, db: DBSession):
    """Initiate password reset. Returns success regardless (prevents email enumeration)."""
    return {"message": "If an account exists with this email, a reset link has been sent."}


@router.post("/reset-password", status_code=200)
async def reset_password(data: ResetPasswordRequest, db: DBSession):
    """Reset password with a valid reset token."""
    payload = verify_token(data.token)
    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    import uuid

    result = await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password has been reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    """Get the currently authenticated user's profile."""
    return current_user


@router.post("/logout", status_code=200)
async def logout():
    """Log out the current user."""
    return {"message": "Logged out successfully"}
