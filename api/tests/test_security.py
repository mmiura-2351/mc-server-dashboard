"""Tests for security utilities."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import JWTError, jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password() -> None:
    """Test password hashing."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
    assert hashed.startswith("$2b$")  # bcrypt format


def test_verify_password() -> None:
    """Test password verification."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_default_expiry() -> None:
    """Test access token creation with default expiry."""
    data = {"sub": "123"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify
    decoded = decode_token(token)
    assert decoded["sub"] == "123"
    assert "exp" in decoded


def test_create_access_token_custom_expiry() -> None:
    """Test access token creation with custom expiry."""
    data = {"sub": "123"}
    custom_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=custom_delta)

    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify
    decoded = decode_token(token)
    assert decoded["sub"] == "123"
    assert "exp" in decoded

    # Verify the expiry is approximately correct (within 5 seconds tolerance)
    expected_exp = datetime.now(UTC) + custom_delta
    actual_exp = datetime.fromtimestamp(decoded["exp"], tz=UTC)
    assert abs((expected_exp - actual_exp).total_seconds()) < 5


def test_create_refresh_token() -> None:
    """Test refresh token creation."""
    data = {"sub": "123"}
    token = create_refresh_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify
    decoded = decode_token(token)
    assert decoded["sub"] == "123"
    assert "exp" in decoded


def test_decode_token() -> None:
    """Test token decoding."""
    data = {"sub": "123", "role": "user"}
    token = create_access_token(data)

    decoded = decode_token(token)
    assert decoded["sub"] == "123"
    assert decoded["role"] == "user"
    assert "exp" in decoded


def test_decode_invalid_token() -> None:
    """Test decoding invalid token."""
    with pytest.raises(JWTError):
        decode_token("invalid_token")


def test_decode_expired_token() -> None:
    """Test decoding expired token."""
    from app.core.config import settings

    # Create a token that expired 1 hour ago
    data = {"sub": "123"}
    expired_time = datetime.now(UTC) - timedelta(hours=1)
    to_encode = data.copy()
    to_encode["exp"] = expired_time

    expired_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(JWTError):
        decode_token(expired_token)
