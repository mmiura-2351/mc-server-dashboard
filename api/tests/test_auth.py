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
