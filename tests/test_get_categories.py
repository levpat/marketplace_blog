import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.users.models import Users


@pytest.mark.asyncio
async def test_get_categories(
        client: AsyncClient,
        get_test_user,
):
    login_data = {
        "username": "johndoe",
        "password": "testpassword",
    }

    login_response = await client.post(
        url="/auth/login",
        json=login_data
    )

    token = login_response.json()["token"]
    cookie = {
        "key": "access_token",
        "value": token,
    }

    get_categories_response = await client.get(
        url="/categories/",
        cookies=cookie
    )

    assert get_categories_response.status_code == 200
    assert len(get_categories_response.json()["categories"]) == 0


@pytest.mark.asyncio
async def test_get_some_categories(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession
):

    async with get_test_session.begin_nested():
        test_category = Category(
            title="Test category",
        )
        get_test_session.add(test_category)
        await get_test_session.flush()
        await get_test_session.refresh(test_category)

    login_data = {
        "username": "johndoe",
        "password": "testpassword",
    }

    login_response = await client.post(
        url="/auth/login",
        json=login_data
    )

    token = login_response.json()["token"]
    cookie = {
        "key": "access_token",
        "value": token,
    }

    categories_response = await client.get(
        url="/categories/",
        cookies=cookie
    )
    assert categories_response.status_code == 200
    assert len(categories_response.json()["categories"]) == 1
