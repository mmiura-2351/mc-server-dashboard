"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import Token, TokenRefresh, UserLogin, UserRegister, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If username or email already exists
    """
    try:
        user = await AuthService.register_user(
            db, user_data.username, user_data.email, user_data.password
        )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    """Authenticate user and return tokens.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        Token: Access and refresh tokens

    Raises:
        HTTPException: If authentication fails or user is not approved
    """
    user = await AuthService.authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not approved yet. Please wait for admin approval.",
        )

    access_token, refresh_token = await AuthService.create_tokens(db, user)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=dict[str, str])
async def refresh(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Refresh access token using refresh token.

    Args:
        token_data: Refresh token data
        db: Database session

    Returns:
        dict: New access token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    access_token = await AuthService.refresh_access_token(db, token_data.refresh_token)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)) -> None:
    """Logout user by revoking refresh token.

    Args:
        token_data: Refresh token data
        db: Database session

    Raises:
        HTTPException: If refresh token is invalid
    """
    success = await AuthService.logout(db, token_data.refresh_token)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
