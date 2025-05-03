from io import BytesIO

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.posts.service import PostService
from src.users.models import Users


@pytest.mark.asyncio
async def test_create_post_success(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession,
        test_post_service: PostService,
        mock_minio_handler,
        test_category_service
):
    test_file = ("test.jpg", BytesIO(b"fake image data"), "image/jpeg")

    async with get_test_session.begin_nested():
        test_category = Category(
            title="Test category",
        )
        get_test_session.add(test_category)
        await get_test_session.flush()
        await get_test_session.refresh(test_category)

    data = {
        "title": "Test post",
        "text": "Test content",
        "categories": ["Test category"],
    }
    files = {
        "image": test_file,
    }

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

    post_response = await client.post(
        url="/posts/",
        cookies=cookie,
        data=data,
        files=files
    )

    assert post_response.status_code == 201