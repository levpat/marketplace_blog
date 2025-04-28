import pytest
from httpx import AsyncClient

from src.users.models import Users
from src.settings.config import bcrypt_context


@pytest.mark.asyncio
async def test_successful_login(
        client: AsyncClient,
):
    test_data = {
        "username": "johndoe",
        "password": "testpassword",
    }

    response = await client.post(
        
    )
