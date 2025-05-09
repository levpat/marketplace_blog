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
    test_data = {
        "category": {"title": "Test category"},
        "post": {
            "title": "Test post",
            "text": "Test content",
            "image_url": "Test_url"
        }
    }

    async with get_test_session.begin_nested():
        category = Category(**test_data["category"])
        get_test_session.add(category)

        post = Post(**test_data["post"])
        get_test_session.add(post)
        await get_test_session.flush()

        get_test_session.add(PostCategories(
            post_id=post.id,
            category_id=category.id
        ))
        await get_test_session.flush()

    login_response = await client.post(
        url="/auth/login",
        json={"username": "johndoe", "password": "testpassword"}
    )
    token = login_response.json()["token"]

    response = await client.get(
        url="/posts/?page=1&page_size=10&categories=Test%20category",
        cookies={"access_token": token}
    )

    assert response.status_code == 200
    response_data = response.json()["data"][0]

    expected_fields = {
        "title": test_data["post"]["title"],
        "text": test_data["post"]["text"],
        "id": str(post.id),
        "image_url": test_data["post"]["image_url"]
    }

    for field, value in expected_fields.items():
        assert response_data[field] == value

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


@pytest.mark.asyncio
async def test_get_posts_with_search(
        client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession
):
    categories = [
        {"title": "Test category"},
        {"title": "Category"}
    ]

    posts = [
        {"title": "Test post A", "text": "Test content A", "image_url": "test_url_A"},
        {"title": "Test post B", "text": "Test content B", "image_url": "test_url_B"},
        {"title": "Test post C", "text": "Test content C", "image_url": "test_url_C"},
        {"title": "Test post D", "text": "Test content D", "image_url": "test_url_D"},
        {"title": "Test post E", "text": "Test content E", "image_url": "test_url_E"},
        {"title": "Test post F", "text": "Test content F", "image_url": "test_url_F"},
        {"title": "Test post G", "text": "Test content G", "image_url": "test_url_G"},
        {"title": "Test post H", "text": "Test content H", "image_url": "test_url_H"},
        {"title": "Test post I", "text": "Test content I", "image_url": "test_url_I"},
        {"title": "Test post J", "text": "Test content J", "image_url": "test_url_J"},
        {"title": "Test post K", "text": "Test content K", "image_url": "test_url_K"},
        {"title": "Test post L", "text": "Test content L", "image_url": "test_url_L"},
        {"title": "Test post M", "text": "Test content M", "image_url": "test_url_M"},
    ]

    post_categories = [
        {"post_title": "Test post A", "category_id": 1},
        {"post_title": "Test post B", "category_id": 1},
        {"post_title": "Test post C", "category_id": 1},
        {"post_title": "Test post D", "category_id": 1},
        {"post_title": "Test post E", "category_id": 1},
        {"post_title": "Test post F", "category_id": 1},
        {"post_title": "Test post G", "category_id": 1},
        {"post_title": "Test post H", "category_id": 1},
        {"post_title": "Test post I", "category_id": 1},
        {"post_title": "Test post J", "category_id": 1},
        {"post_title": "Test post K", "category_id": 1},
        {"post_title": "Test post L", "category_id": 2},
        {"post_title": "Test post M", "category_id": 2},
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
        url="/posts/?page=1&page_size=10&categories=Test%20category&search=Test%20post",
        cookies={"access_token": token}
    )

    assert post_response.status_code == 200
    response_data = post_response.json()["data"]
    assert len(response_data) == 10


    for post, expected in zip(
            [response_data[i] for i in range(len(response_data))],
            [posts[j] for j in range(len(posts))]):
        assert post["title"] == expected["title"]
        assert post["text"] == expected["text"]
        assert post["id"] == post_ids[expected["title"]]
        assert post["image_url"] == expected["image_url"]
        assert post["created_at"] is not None
        assert post["updated_at"] is None

    post_response = await client.get(
        url="/posts/?page=2&page_size=10&categories=Test%20category&search=Test%20post",
        cookies={"access_token": token}
    )

    assert post_response.status_code == 200
    response_data = post_response.json()["data"]
    assert len(response_data) == 1

    for post, expected in zip(
            [response_data[0]],
            [posts[10]]):
        assert post["title"] == expected["title"]
        assert post["text"] == expected["text"]
        assert post["id"] == post_ids[expected["title"]]
        assert post["image_url"] == expected["image_url"]
        assert post["created_at"] is not None
        assert post["updated_at"] is None

@pytest.mark.asyncio
async def test_get_posts_without_category(
client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession
):
    login_response = await client.post(
        url="/auth/login",
        json={"username": "johndoe", "password": "testpassword"}
    )

    token = login_response.json()["token"]

    post_response = await client.get(
        url="/posts/?page=1&page_size=10",
        cookies={"access_token": token}
    )

    assert post_response.status_code == 400
    assert post_response.json()["detail"] == "Need to add categories"

@pytest.mark.asyncio
async def test_get_posts_with_wrong_categories(
client: AsyncClient,
        get_test_user: Users,
        get_test_session: AsyncSession
):
    categories = [
        {"title": "Test category"},
        {"title": "Category"}
    ]

    async with get_test_session.begin_nested():
        for category in categories:
            test_category = Category(**category)
            get_test_session.add(test_category)
        await get_test_session.flush()

    login_response = await client.post(
        url="/auth/login",
        json={"username": "johndoe", "password": "testpassword"}
    )

    token = login_response.json()["token"]

    post_response = await client.get(
        url="/posts/?page=1&page_size=10&categories=Test",
        cookies={"access_token": token}
    )

    assert post_response.status_code == 404
    assert post_response.json()["detail"] == "Some categories not found"