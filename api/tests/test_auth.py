"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole

client = TestClient(app)


@pytest.mark.asyncio
async def test_register_user_success(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_register_duplicate_username(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_register_duplicate_email(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_login_success(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_login_unapproved_user(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_login_wrong_password(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_login_nonexistent_user(db_session: AsyncSession, override_get_db: None) -> None:
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/login", json={"username": "nonexistent", "password": "password123"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_success(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_refresh_token_invalid(db_session: AsyncSession, override_get_db: None) -> None:
    """Test token refresh with invalid token."""
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_success(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_logout_invalid_token(db_session: AsyncSession, override_get_db: None) -> None:
    """Test logout with invalid token."""
    response = client.post("/api/v1/auth/logout", json={"refresh_token": "invalid_token"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_inactive_user(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_refresh_token_expired(db_session: AsyncSession, override_get_db: None) -> None:
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
async def test_create_tokens_revokes_existing_tokens(
    db_session: AsyncSession, override_get_db: None
) -> None:
    """Test that creating new tokens revokes existing active tokens."""
    import asyncio

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

    # Create first tokens
    access_token1, refresh_token1 = await AuthService.create_tokens(db_session, user)
    assert access_token1 is not None
    assert refresh_token1 is not None

    # Verify one token exists and is active
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    tokens = result.scalars().all()
    assert len(tokens) == 1
    assert tokens[0].is_revoked is False

    # Wait 1 second to ensure JWT exp timestamp is different
    # (JWT tokens with same user_id and exp generate identical token strings)
    await asyncio.sleep(1.0)

    # Create second tokens (should revoke first)
    access_token2, refresh_token2 = await AuthService.create_tokens(db_session, user)
    assert access_token2 is not None
    assert refresh_token2 is not None
    assert refresh_token2 != refresh_token1

    # Refresh the first token object to see updated state
    await db_session.refresh(tokens[0])

    # Verify first token is now revoked
    assert tokens[0].is_revoked is True

    # Verify we have 2 tokens total: 1 revoked, 1 active
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    all_tokens = result.scalars().all()
    assert len(all_tokens) == 2

    revoked_count = sum(1 for t in all_tokens if t.is_revoked)
    active_count = sum(1 for t in all_tokens if not t.is_revoked)
    assert revoked_count == 1
    assert active_count == 1


