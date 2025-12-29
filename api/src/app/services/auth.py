"""Authentication service for user registration, login, and token management."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import RefreshToken, User, UserRole


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    async def register_user(db: AsyncSession, username: str, email: str, password: str) -> User:
        """Register a new user.

        Args:
            db: Database session
            username: User's username
            email: User's email
            password: Plain text password

        Returns:
            User: Created user object

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")

        # Check if email already exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ValueError("Email already exists")

        # Create new user
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.USER,
            is_active=True,
            is_approved=False,  # Requires admin approval
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        """Authenticate user by username and password.

        Args:
            db: Database session
            username: User's username
            password: Plain text password

        Returns:
            User | None: User object if authentication successful, None otherwise
        """
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    async def create_tokens(db: AsyncSession, user: User) -> tuple[str, str]:
        """Create access and refresh tokens for a user.

        Args:
            db: Database session
            user: User object

        Returns:
            tuple[str, str]: (access_token, refresh_token)
        """
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Create refresh token
        refresh_token_str = create_refresh_token(data={"sub": str(user.id)})

        # Store refresh token in database
        from app.core.config import settings

        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Revoke existing refresh tokens for this user
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user.id, ~RefreshToken.is_revoked)
        )
        existing_tokens = result.scalars().all()
        for token in existing_tokens:
            token.is_revoked = True

        # Create new refresh token
        refresh_token = RefreshToken(
            token=refresh_token_str, user_id=user.id, expires_at=expires_at, is_revoked=False
        )
        db.add(refresh_token)
        await db.commit()

        return access_token, refresh_token_str

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> str | None:
        """Refresh access token using a refresh token.

        Args:
            db: Database session
            refresh_token_str: Refresh token string

        Returns:
            str | None: New access token if successful, None otherwise
        """
        # Find refresh token in database
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        )
        refresh_token = result.scalar_one_or_none()

        if not refresh_token:
            return None

        # Check if token is revoked
        if refresh_token.is_revoked:
            return None

        # Check if token is expired
        if refresh_token.expires_at < datetime.now(UTC):
            return None

        # Create new access token
        access_token = create_access_token(data={"sub": str(refresh_token.user_id)})
        return access_token

    @staticmethod
    async def logout(db: AsyncSession, refresh_token_str: str) -> bool:
        """Logout user by revoking refresh token.

        Args:
            db: Database session
            refresh_token_str: Refresh token string

        Returns:
            bool: True if logout successful, False otherwise
        """
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        )
        refresh_token = result.scalar_one_or_none()

        if not refresh_token:
            return False

        refresh_token.is_revoked = True
        await db.commit()
        return True
