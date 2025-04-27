import asyncio
import pytest_asyncio
from typing import AsyncGenerator

from faststream.redis import TestRedisBroker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from src.main import app
from src.settings.config import test_db_url
from src.users.repository import UserRepository
from src.users.service import UserService, get_user_service

test_engine: AsyncEngine = create_async_engine(
    test_db_url,
    echo=True
)

test_async_session = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)


class TestBase(DeclarativeBase):
    pass


@pytest_asyncio.fixture(scope="module", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)
        await conn.run_sync(TestBase.metadata.create_all)
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)


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


# async def mock_broker():
#    with patch("src.users.service.broker") as mock_broker:
#        mock_broker.connect = AsyncMock()
#        mock_broker.is_connected = True
#        mock_broker.publish = AsyncMock()
#        mock_broker.subscriber = MagicMock()
#        mock_broker.subscriber.return_value = lambda fn: fn
#        yield mock_broker


@pytest_asyncio.fixture(scope="function")
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session


@pytest_asyncio.fixture
async def test_user_repository(get_test_session: AsyncSession):
    return UserRepository(get_test_session)


@pytest_asyncio.fixture
async def test_user_service(get_test_session: AsyncSession):
    return UserService(UserRepository(get_test_session))
