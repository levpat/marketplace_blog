import asyncio
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker

from src.settings.config import test_db_url
from src.backend.db import Base
from src.users.repository import UserRepository

engine: AsyncEngine = create_async_engine(
    test_db_url,
    echo=True
)

test_async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)


@pytest_asyncio.fixture(scope="module", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def user_repository(get_session: AsyncSession):
    return UserRepository(get_session)
