import pytest

from src.users.repository import UserRepository
from src.settings.config import bcrypt_context


@pytest.mark.asyncio
async def test_create_user(
        user_repository: UserRepository
):
    users = await user_repository.create(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email="johndoe@example.com",
        password=bcrypt_context.hash("testpassword")
    )

    assert len(users) == 1

    user = users[0]

    assert user.id is not None
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.username == "johndoe"
    assert user.email == "johndoe@example.com"
    assert bcrypt_context.verify("testpassword", user.hashed_password)
    assert user.role == "user"
