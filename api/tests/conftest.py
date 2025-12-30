"""Pytest configuration and fixtures."""

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine with proper cleanup.

    Yields:
        AsyncEngine: Test database engine
    """
    # Test database URL (in-memory SQLite for testing)
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    yield engine

    # CRITICAL: Dispose engine to cleanup connection pool and background threads
    engine.sync_engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create test session factory.

    Args:
        test_engine: Test database engine

    Returns:
        async_sessionmaker: Test session factory
    """
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(test_engine, test_session_factory) -> AsyncGenerator[AsyncSession]:
    """Create a test database session.

    Args:
        test_engine: Test database engine
        test_session_factory: Test session factory

    Yields:
        AsyncSession: Test database session
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with test_session_factory() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency for testing.

    Args:
        db_session: Test database session

    Yields:
        None
    """

    async def _get_test_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    yield

    # CRITICAL: Clear dependency overrides after test to prevent state leakage
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create TestClient with proper resource cleanup.

    Yields:
        TestClient: FastAPI test client
    """
    # CRITICAL: Use context manager to ensure proper cleanup
    with TestClient(app) as c:
        yield c
