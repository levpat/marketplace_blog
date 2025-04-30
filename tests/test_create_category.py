import pytest
from httpx import AsyncClient


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
