import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.associations.models import PostCategories
from src.categories.models import Category
from src.users.models import Users
from src.posts.models import Post


@pytest.mark.asyncio
async def test_get_all_posts_without_search(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession
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
            image_url="Test_url"
        )
        get_test_session.add(test_post)
        await get_test_session.flush()
        await get_test_session.refresh(test_post)

    async with get_test_session.begin_nested():
        get_post_id = await get_test_session.scalar(
            select(Post.id).where(Post.title == "Test post")
        )

    async with get_test_session.begin_nested():
        test_post_category = PostCategories(
            post_id=get_post_id,
            category_id=1
        )
        get_test_session.add(test_post_category)
        await get_test_session.flush()
        await get_test_session.refresh(test_post_category)

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

    post_response = await client.get(
        url="/posts/?page=1&page_size=10&categories=Test%20category",
        cookies=cookie
    )

    assert post_response.status_code == 200
    response_data = post_response.json()["data"][0]
    assert response_data["title"] == "Test post"
    assert response_data["text"] == "Test content"
    assert response_data["id"] == str(get_post_id)
    assert response_data["image_url"] == "Test_url"
    assert response_data["created_at"] is not None
    assert response_data["updated_at"] is None
