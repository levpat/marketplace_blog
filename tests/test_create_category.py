import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.users.models import Users


@pytest.mark.asyncio
async def test_create_category(
        client: AsyncClient,
        get_test_user
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

    test_data = {
        "title": "Test category",
    }

    category_response = await client.post(
        url="/categories/create",
        json=test_data,
        cookies=cookie
    )

    assert category_response.status_code == 201

    response_data = category_response.json()
    assert response_data["id"] == 1
    assert response_data["title"] == "Test category"


@pytest.mark.asyncio
async def test_create_same_category(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession,
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

    test_data = {
        "title": "Test category",
    }

    category_response = await client.post(
        url="/categories/create",
        json=test_data,
        cookies=cookie
    )

    assert category_response.status_code == 400

    response_data = category_response.json()
    assert response_data["detail"] == "This category is already exist"
