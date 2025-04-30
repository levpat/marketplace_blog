import pytest
from httpx import AsyncClient

from src.users.models import Users
from src.settings.config import bcrypt_context


@pytest.mark.asyncio
async def test_successful_login(
        client: AsyncClient,
        get_test_user
):
    test_data = {
        "username": "johndoe",
        "password": "testpassword",
    }

    response = await client.post(
        "/auth/login",
        json=test_data,
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["detail"] == "Wellcome John!"
    assert response_data["token"] is not None


@pytest.mark.asyncio
async def test_login_with_wrong_username(
        client: AsyncClient,
        get_test_user
):
    test_data = {
        "username": "John",
        "password": "testpassword"
    }

    response = await client.post(
        "auth/login",
        json=test_data
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_login_with_wrong_password(
        client: AsyncClient,
        get_test_user
):
    test_data = {
        "username": "johndoe",
        "password": "test_password"
    }

    response = await client.post(
        "auth/login",
        json=test_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Wrong password"
