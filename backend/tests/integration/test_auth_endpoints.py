import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models.user import User

@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient, db):
    # 1. Register a new user
    reg_data = {
        "email": "testuser@example.com",
        "password": "strongpassword123",
        "full_name": "Test User",
        "role": "admin"
    }
    
    response = await client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 201
    res_data = response.json()
    assert "access_token" in res_data
    assert "refresh_token" in res_data
    assert res_data["token_type"] == "bearer"
    
    access_token = res_data["access_token"]
    refresh_token = res_data["refresh_token"]

    # Verify user actually exists in the database
    result = await db.execute(select(User).where(User.email == "testuser@example.com"))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.full_name == "Test User"
    assert db_user.role == "admin"

    # 2. Try to register the same user again (conflict)
    response_dup = await client.post("/api/v1/auth/register", json=reg_data)
    assert response_dup.status_code == 400
    assert "already registered" in response_dup.json()["detail"]

    # 3. Login with the user
    login_data = {
        "email": "testuser@example.com",
        "password": "strongpassword123"
    }
    response_login = await client.post("/api/v1/auth/login", json=login_data)
    assert response_login.status_code == 200
    login_res = response_login.json()
    assert "access_token" in login_res
    assert "refresh_token" in login_res
    
    # 4. Get the authenticated user's profile
    headers = {"Authorization": f"Bearer {access_token}"}
    response_me = await client.get("/api/v1/auth/me", headers=headers)
    assert response_me.status_code == 200
    me_data = response_me.json()
    assert me_data["email"] == "testuser@example.com"
    assert me_data["full_name"] == "Test User"

    # 5. Refresh token
    refresh_data = {
        "refresh_token": refresh_token
    }
    response_refresh = await client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response_refresh.status_code == 200
    refresh_res = response_refresh.json()
    assert "access_token" in refresh_res
    assert "refresh_token" in refresh_res
