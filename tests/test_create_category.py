import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(
        client: AsyncClient,
):
    test_data = {
        "title": "Test category",
    }

    response = await client.post(
        url="/categories/create",
        json=test_data
    )

    assert response.status_code == 201
