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

    post_response = await client.put(
        url="/posts/",
        cookies=cookie,
        data=data,
        files=files
    )

    assert post_response.status_code == 201
    response_data = post_response.json()
    post_response_data = post_response.json()["data"][0]
    assert response_data["detail"] == "Post updated"
    assert post_response_data["title"] == "Updated test post"
    assert post_response_data["text"] == "Updated test content"
    assert post_response_data["id"] is not None
    assert post_response_data["image_url"] == "http://127.0.0.1:9000/marketplace-blog/test.jpg"
    assert post_response_data["created_at"] is not None
    assert post_response_data["updated_at"] is not None


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
