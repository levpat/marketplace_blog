from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_session
from src.users.models import Users


class UserRepository:
    def __init__(self,
                 session: AsyncSession):
        self.session = session

    async def create(self,
                     first_name: str,
                     last_name: str,
                     username: str,
                     email: str,
                     password: str) -> list[Users]:
        user = Users(first_name=first_name,
                     last_name=last_name,
                     username=username,
                     email=email,
                     hashed_password=password)
        self.session.add(user)
        await self.session.commit()
        return [user]

    async def get_user_for_authenticate(self,
                                        username: str) -> Users:
        user = await self.session.scalar(select(Users) \
                                         .where(username == Users.username))
        return user


def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    return UserRepository(session)
