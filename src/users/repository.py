from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, or_
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
        current_user = await self.session.scalar(
            select(Users).where(or_(
                Users.email == email,
                Users.username == username
            )
            )
        )

        if current_user is None:
            new_user = Users(first_name=first_name,
                             last_name=last_name,
                             username=username,
                             email=email,
                             hashed_password=password)
            self.session.add(new_user)
            await self.session.commit()
            return [new_user]

        if current_user.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has been registered"
            )

        if current_user.username == username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is taken"
            )

    async def get_user_for_authenticate(self,
                                        username: str) -> Users:
        user = await self.session.scalar(select(Users) \
                                         .where(Users.username == username))
        return user


def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    return UserRepository(session)
