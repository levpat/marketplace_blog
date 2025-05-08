from io import BytesIO
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.posts.models import Post
from src.users.models import Users


@pytest.mark.asyncio
async def test_update_post_success(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession,
        mock_minio_handler,
):
    test_data = {
        "category": {"title": "Test category"},
        "post": {
            "title": "Test post",
            "text": "Test content",
            "image_url": "Test_url"
        },
        "update_data": {
            "title": "Updated test post",
            "text": "Updated test content",
            "categories": ["Test category"]
        },
        "file": ("test.jpg", BytesIO(b"fake image data"), "image/jpeg")
    }

    async with get_test_session.begin_nested():
        category = Category(**test_data["category"])
        post = Post(**test_data["post"])

        get_test_session.add_all([category, post])
        await get_test_session.flush()

    data = {
        "post_id": str(post.id),
        **test_data["update_data"]
    }

    login_response = await client.post(
        url="/auth/login",
        json={"username": "johndoe", "password": "testpassword"}
    )
    token = login_response.json()["token"]

    response = await client.put(
        url="/posts/",
        cookies={"access_token": token},
        data=data,
        files={"image": test_data["file"]}
    )

    assert response.status_code == 201
    response_data = response.json()

    def get_nested_value(data, path):
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, list):
                key = int(key)
            current = current[key]
        return current

    expected_fields = {
        "detail": "Post updated",
        "data.0.title": test_data["update_data"]["title"],
        "data.0.text": test_data["update_data"]["text"],
        "data.0.image_url": "http://127.0.0.1:9000/marketplace-blog/test.jpg"
    }

    for path, expected_value in expected_fields.items():
        assert get_nested_value(response_data, path) == expected_value

    post_data = response_data["data"][0]
    assert post_data["id"] == str(post.id)
    assert post_data["created_at"] is not None
    assert post_data["updated_at"] is not None


@pytest.mark.asyncio
async def test_update_post_without_category(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession,
        mock_minio_handler,
):
    test_file = ("test.jpg", BytesIO(b"fake image data"), "image/jpeg")

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

    data = {
        "post_id": str(get_post_id),
        "title": "Updated test post",
        "text": "Updated test content",
        "categories": [""],
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

    assert post_response.status_code == 404
    response_data = post_response.json()
    assert response_data["detail"] == "Some categories not found"


@pytest.mark.asyncio
async def test_update_post_with_same_title(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession,
        mock_minio_handler
):
    test_file = ("test.jpg", BytesIO(b"fake image data"), "image/jpeg")

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

    data = {
        "post_id": str(get_post_id),
        "title": "Test post",
        "text": "Updated test content",
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

    assert post_response.status_code == 400
    assert post_response.json()["detail"] == "Post with same title is already exist"


@pytest.mark.asyncio
async def test_update_post_with_same_text(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession,
        mock_minio_handler,
):
    test_file = ("test.jpg", BytesIO(b"fake image data"), "image/jpeg")

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

    data = {
        "post_id": str(get_post_id),
        "title": "Updated test post",
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

    assert post_response.status_code == 400
    assert post_response.json()["detail"] == "Post with same text is already exist"
