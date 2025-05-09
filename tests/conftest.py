import asyncio
from unittest.mock import AsyncMock

import pytest_asyncio
from typing import AsyncGenerator

from faststream.redis import TestRedisBroker
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from src.backend.db import Base
from src.auth.service import AuthService, get_auth_service
from src.categories.repository import CategoryRepository
from src.categories.service import CategoryService, get_category_service
from src.main import app
from src.posts.repository import PostRepository
from src.posts.service import PostService, get_post_service
from src.posts.utils import MinioHandler
from src.settings.config import get_settings
from src.users.models import Users
from src.users.repository import UserRepository
from src.users.service import UserService, get_user_service

test_engine: AsyncEngine = create_async_engine(
    get_settings().test_db_url,
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
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await asyncio.sleep(0.1)
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


@pytest_asyncio.fixture(autouse=True)
async def override_auth_dependencies(test_authenticate_service: AuthService):
    original_get_auth_service = app.dependency_overrides.get(get_auth_service)

    def _get_test_auth_service():
        return test_authenticate_service

    app.dependency_overrides[get_auth_service] = _get_test_auth_service
    yield

    if original_get_auth_service:
        app.dependency_overrides[get_auth_service] = original_get_auth_service
    else:
        del app.dependency_overrides[get_auth_service]


@pytest_asyncio.fixture(autouse=True)
async def override_category_dependencies(test_category_service: CategoryService):
    original_get_category_service = app.dependency_overrides.get(get_category_service)

    def _get_test_category_service():
        return test_category_service

    app.dependency_overrides[get_category_service] = _get_test_category_service
    yield

    if original_get_category_service:
        app.dependency_overrides[get_category_service] = original_get_category_service
    else:
        del app.dependency_overrides[get_category_service]


@pytest_asyncio.fixture(autouse=True)
async def override_post_dependencies(test_post_service: PostService):
    original_get_post_service = app.dependency_overrides.get(get_post_service)

    def _get_test_post_service():
        return test_post_service

    app.dependency_overrides[get_post_service] = _get_test_post_service
    yield

    if original_get_post_service:
        app.dependency_overrides[get_post_service] = original_get_post_service
    else:
        del app.dependency_overrides[get_post_service]


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test",
            follow_redirects=True,
            cookies={}
    ) as client:
        yield client


@pytest_asyncio.fixture
async def mock_minio_handler(monkeypatch):
    mock = AsyncMock(spec=MinioHandler)
    mock.upload_file = AsyncMock(return_value=None)
    mock.get_upload_image_url = AsyncMock(return_value="http://minio-test/test.jpg")
    monkeypatch.setattr(
        "src.posts.utils.get_minio_handler",
        AsyncMock(return_value=mock)
    )
    return mock


@pytest_asyncio.fixture(autouse=True)
async def test_broker():
    from src.users.service import broker

    async with TestRedisBroker(broker=broker) as test_broker:
        yield test_broker


@pytest_asyncio.fixture(scope="function")
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()


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
async def test_category_service(
        get_test_session: AsyncSession,
):
    return CategoryService(CategoryRepository(get_test_session))


@pytest_asyncio.fixture
async def test_post_service(
        get_test_session: AsyncSession,
        mock_minio_handler: AsyncMock,
):
    return PostService(
        repository=PostRepository(get_test_session),
        client=mock_minio_handler
    )


@pytest_asyncio.fixture
async def get_test_user(get_test_session):
    async with get_test_session.begin():
        test_user = Users(
            username="johndoe",
            hashed_password=get_settings().bcrypt_context.hash("testpassword"),
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
        get_test_session.add(test_user)
        await get_test_session.flush()
        await get_test_session.refresh(test_user)
        yield test_user
