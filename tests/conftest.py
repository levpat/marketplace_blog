import asyncio
import pytest_asyncio
from typing import AsyncGenerator

from faststream.redis import TestRedisBroker
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from src.backend.db import Base
from src.auth.service import AuthService
from src.main import app
from src.settings.config import test_db_url, bcrypt_context
from src.users.models import Users
from src.users.repository import UserRepository
from src.users.service import UserService, get_user_service

test_engine: AsyncEngine = create_async_engine(
    test_db_url,
    echo=True,
    poolclass=NullPool
)

test_async_session = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def _get_test_session():
    async with test_async_session() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_user_dependencies(test_user_service: UserService):
    original_get_user_service = app.dependency_overrides.get(get_user_service)

    def _get_test_user_service():
        return test_user_service

    app.dependency_overrides[get_user_service] = _get_test_user_service
    yield

    if original_get_user_service:
        app.dependency_overrides[get_user_service] = original_get_user_service
    else:
        del app.dependency_overrides[get_user_service]


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def test_broker():
    from src.users.service import broker

    async with TestRedisBroker(broker=broker) as test_broker:
        yield test_broker


@pytest_asyncio.fixture(scope="function")
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session


@pytest_asyncio.fixture
async def test_user_repository(
        get_test_session: AsyncSession
):
    return UserRepository(get_test_session)


@pytest_asyncio.fixture
async def test_user_service(
        get_test_session: AsyncSession
):
    return UserService(UserRepository(get_test_session))


@pytest_asyncio.fixture
async def test_authenticate_service(
        get_test_session: AsyncSession
):
    return AuthService(UserRepository(get_test_session))


@pytest_asyncio.fixture
async def get_test_user(
        get_test_session
):
    test_user = Users(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email="test@example.com",
        hashed_password=bcrypt_context.hash("testpassword")
    )
    get_test_session.add(test_user)
    await get_test_session.commit()
    yield test_user
    await get_test_session.close()

    await get_test_session.rollback()
