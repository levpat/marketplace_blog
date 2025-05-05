import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.posts.models import Post
from src.users.models import Users


@pytest.mark.asyncio
async def test_delete_post_success(
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

    async with get_test_session.begin_nested():
        test_post = Post(
            title="Test post",
            text="Test content",
            image_url="Test_url",
        )
        get_test_session.add(test_post)
        await get_test_session.flush()
        await get_test_session.refresh(test_post)

    async with get_test_session.begin_nested():
        get_post_id = await get_test_session.scalar(
            select(Post.id)
            .where(Post.title == "Test post")
        )

    data = {
        "post_id": str(get_post_id)
    }

    login_data = {
        "username": "johndoe",
        "password": "testpassword",
    }

    login_response = await client.post(
        url="/auth/login",
        json=login_data,
    )

    token = login_response.json()["token"]

    cookie = {
        "key": "access_token",
        "value": token,
    }

    delete_response = await client.delete(
        url="/posts/",
        cookies=cookie,
        params=data,
    )

    assert delete_response.status_code == 200
    data = delete_response.json()["data"][0]
    assert data["title"] == "Test post"
    assert data["text"] == "Test content"
    assert data["id"] == str(get_post_id)
    assert data["image_url"] == "Test_url"
    assert data["created_at"] is not None


@pytest.mark.asyncio
async def test_delete_post_with_wrong_post_id(
        client: AsyncClient,
        get_test_user: Users,
):
    data = {
        "post_id": str(uuid.uuid4()),
    }

    login_data = {
        "username": "johndoe",
        "password": "testpassword",
    }

    login_response = await client.post(
        url="/auth/login",
        json=login_data,
    )

    token = login_response.json()["token"]

    cookie = {
        "key": "access_token",
        "value": token
    }

    delete_response = await client.delete(
        url="/posts/",
        cookies=cookie,
        params=data,
    )

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Post not found"
