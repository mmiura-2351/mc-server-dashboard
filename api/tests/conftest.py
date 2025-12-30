"""Pytest configuration and fixtures."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def worker_id(request: pytest.FixtureRequest) -> str:
    """Get worker ID for parallel test execution.

    Args:
        request: Pytest fixture request

    Returns:
        str: Worker ID (e.g., 'gw0', 'gw1') or 'master' for non-parallel execution
    """
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput["workerid"]
    return "master"


@pytest.fixture(scope="session")
def test_engine(worker_id: str):
    """Create test database engine for each worker.

    Args:
        worker_id: Worker ID for parallel execution

    Returns:
        AsyncEngine: Test database engine
    """
    # Use file-based SQLite with worker-specific database file for parallel execution
    # This ensures each worker has its own isolated database
    test_db_url = f"sqlite+aiosqlite:///test_{worker_id}.db"
    engine = create_async_engine(test_db_url, echo=False)
    yield engine
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

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db(db_session: AsyncSession) -> None:
    """Override get_db dependency for testing.

    Args:
        db_session: Test database session
    """

    async def _get_test_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
