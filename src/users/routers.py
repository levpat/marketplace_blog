from fastapi import APIRouter, Depends, status
from sqlalchemy import insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.backend.db_depends import get_db
from src.users.models import Users
from src.users.schemas import CreateUser
from src.auth.backend import send_email

user_router = APIRouter(prefix='/users', tags=['users'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)],
                      create_user: CreateUser) -> dict:
    await db.execute(insert(Users).values(first_name=create_user.first_name,
                                          last_name=create_user.last_name,
                                          username=create_user.username,
                                          email=create_user.email,
                                          hashed_password=bcrypt_context.hash(create_user.password)
                                          ))
    await db.commit()

    await send_email(create_user.email)

    return {
        'status_code': status.HTTP_201_CREATED,
        'transactions': 'Success'
    }
