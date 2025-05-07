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


@pytest.mark.asyncio
async def test_get_posts_with_same_categories(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession
):
    categories = [
        {"title": "Test category"},
        {"title": "Category"}
    ]

    posts = [
        {"title": "First test post", "text": "First test content", "image_url": "First_test_url"},
        {"title": "Second test post", "text": "Second test content", "image_url": "Second_test_url"},
        {"title": "Third test post", "text": "Third test content", "image_url": "Third_test_url"}
    ]

    post_categories = [
        {"post_title": "First test post", "category_id": 1},
        {"post_title": "Second test post", "category_id": 2},
        {"post_title": "Third test post", "category_id": 1}
    ]

    async with get_test_session.begin_nested():
        for category in categories:
            test_category = Category(**category)
            get_test_session.add(test_category)
        await get_test_session.flush()

        post_objects = []
        for post in posts:
            test_post = Post(**post)
            get_test_session.add(test_post)
            post_objects.append(test_post)
        await get_test_session.flush()

        post_titles = [post["title"] for post in posts]
        result = await get_test_session.execute(
            select(Post.id, Post.title).where(Post.title.in_(post_titles))
        )
        post_ids = {title: str(id) for id, title in result.all()}

        for post_category in post_categories:
            post_id = post_ids[post_category["post_title"]]
            get_test_session.add(PostCategories(
                post_id=post_id,
                category_id=post_category["category_id"]
            ))
        await get_test_session.flush()

    login_response = await client.post(
        url="/auth/login",
        json={"username": "johndoe", "password": "testpassword"}
    )
    token = login_response.json()["token"]

    post_response = await client.get(
        url="/posts/?page=1&page_size=10&categories=Test%20category",
        cookies={"access_token": token}
    )

    assert post_response.status_code == 200
    response_data = post_response.json()["data"]

    for post, expected in zip([response_data[0], response_data[-1]], [posts[0], posts[2]]):
        assert post["title"] == expected["title"]
        assert post["text"] == expected["text"]
        assert post["id"] == post_ids[expected["title"]]
        assert post["image_url"] == expected["image_url"]
        assert post["created_at"] is not None
        assert post["updated_at"] is None
