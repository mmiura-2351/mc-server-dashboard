"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_register_user_success(client: TestClient, db_session: AsyncSession) -> None:
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert data["is_approved"] is False
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client: TestClient, db_session: AsyncSession) -> None:
    """Test registration with duplicate username."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test1@example.com", "password": "password123"},
    )

    # Try to register with same username
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test2@example.com", "password": "password123"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(client: TestClient, db_session: AsyncSession) -> None:
    """Test registration with duplicate email."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={"username": "user1", "email": "test@example.com", "password": "password123"},
    )

    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "user2", "email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: TestClient, db_session: AsyncSession) -> None:
    """Test successful login."""
    # Create approved user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_unapproved_user(client: TestClient, db_session: AsyncSession) -> None:
    """Test login with unapproved user."""
    # Create unapproved user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=False,
    )
    db_session.add(user)
    await db_session.commit()

    # Try to login
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password123"}
    )

    assert response.status_code == 403
    assert "not approved" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_wrong_password(client: TestClient, db_session: AsyncSession) -> None:
    """Test login with wrong password."""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: TestClient, db_session: AsyncSession) -> None:
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/login", json={"username": "nonexistent", "password": "password123"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_success(client: TestClient, db_session: AsyncSession) -> None:
    """Test successful token refresh."""
    # Create approved user and login
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: TestClient, db_session: AsyncSession) -> None:
    """Test token refresh with invalid token."""
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_success(client: TestClient, db_session: AsyncSession) -> None:
    """Test successful logout."""
    # Create approved user and login
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Logout
    response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})

    assert response.status_code == 204

    # Try to refresh with revoked token
    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_logout_invalid_token(client: TestClient, db_session: AsyncSession) -> None:
    """Test logout with invalid token."""
    response = client.post("/api/v1/auth/logout", json={"refresh_token": "invalid_token"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_inactive_user(client: TestClient, db_session: AsyncSession) -> None:
    """Test login with inactive user."""
    # Create inactive user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=False,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Try to login
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password123"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_expired(client: TestClient, db_session: AsyncSession) -> None:
    """Test token refresh with expired token."""
    from datetime import UTC, datetime, timedelta

    from app.models.user import RefreshToken

    # Create approved user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create expired refresh token
    expired_token = RefreshToken(
        token="expired_token_string",
        user_id=user.id,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        is_revoked=False,
    )
    db_session.add(expired_token)
    await db_session.commit()

    # Try to refresh with expired token
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "expired_token_string"})

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_tokens_revokes_existing_tokens(db_session: AsyncSession) -> None:
    """Test that creating new tokens revokes existing active tokens."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from app.models.user import RefreshToken
    from app.services.auth import AuthService

    # Create approved user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
        is_active=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Directly create an existing refresh token in database
    # (simulating a token from a previous login)
    existing_token = RefreshToken(
        token="old_refresh_token_string",
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        is_revoked=False,
    )
    db_session.add(existing_token)
    await db_session.commit()

    # Verify one token exists and is active
    result = await db_session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    tokens = result.scalars().all()
    assert len(tokens) == 1
    assert tokens[0].is_revoked is False

    # Create new tokens (should revoke the existing token)
    access_token, refresh_token = await AuthService.create_tokens(db_session, user)
    assert access_token is not None
    assert refresh_token is not None
    assert refresh_token != "old_refresh_token_string"

    # Refresh the existing token object to see updated state
    await db_session.refresh(existing_token)

    # Verify existing token is now revoked
    assert existing_token.is_revoked is True

    # Verify we have 2 tokens total: 1 revoked (old), 1 active (new)
    result = await db_session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    all_tokens = result.scalars().all()
    assert len(all_tokens) == 2

    revoked_count = sum(1 for t in all_tokens if t.is_revoked)
    active_count = sum(1 for t in all_tokens if not t.is_revoked)
    assert revoked_count == 1
    assert active_count == 1
