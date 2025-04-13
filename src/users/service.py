from typing import Annotated
from fastapi import Depends, status
from passlib.context import CryptContext

from src.users.models import Users
from src.users.repository import UserRepository, get_user_repository
from src.users.schemas import CreateUserSchema

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService:
    def __init__(self,
                 repository: UserRepository):
        self.repository = repository

    async def create(self,
                     create_user: CreateUserSchema
                     ) -> list[Users]:
        user = await self.repository.create(first_name=create_user.first_name,
                                            last_name=create_user.last_name,
                                            username=create_user.username,
                                            email=create_user.email,
                                            password=bcrypt_context.hash(create_user.password))

        return user


def get_user_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(repository)
