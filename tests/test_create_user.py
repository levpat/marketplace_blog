import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(
        client: AsyncClient,
):
    test_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "test@example.com",
        "password": "testpaassword"
    }

    response = await client.post(
        "/users/",
        json=test_data,
    )

    assert response.status_code == 201

    response_data = response.json()
    assert response_data["status_code"] == 201
    assert response_data["detail"] == "User create"

    data = response_data["data"][0]
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["username"] == "johndoe"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_with_registered_email(
        client: AsyncClient,
        get_test_user
):
    test_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "doejohn",
        "email": "test@example.com",
        "password": "testpaassword"
    }

    response = await client.post(
        "/users/",
        json=test_data,
    )

    assert response.status_code == 400

    response_data = response.json()
    assert response_data["detail"] == "This email has been registered"


@pytest.mark.asyncio
async def test_create_user_with_registered_username(
        client: AsyncClient,
        get_test_user
):
    test_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "example@test.com",
        "password": "testpaassword"
    }

    response = await client.post(
        "/users/",
        json=test_data,
    )

    assert response.status_code == 400

    response_data = response.json()
    assert response_data["detail"] == "This username is taken"
