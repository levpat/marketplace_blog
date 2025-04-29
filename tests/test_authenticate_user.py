import pytest
# from fastapi.testclient import TestClient
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

