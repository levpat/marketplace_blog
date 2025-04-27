import pytest
from faststream.redis import TestRedisBroker
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from fastapi import status

from src.main import app
from src.users.repository import UserRepository
from src.settings import config
from src.users.service import UserService, handle_email_task


@pytest.mark.asyncio
async def test_create_user(
        client: AsyncClient,
        test_broker: TestRedisBroker,
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

    print("Validation errors:", response.json())
    assert response.status_code == 200
