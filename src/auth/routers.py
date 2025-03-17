from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.backend.db_depends import get_db
from src.users.models import Users

auth_router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)],
                            username: str, password: str):
    user = await db.scalar(select(Users).where(Users.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


@auth_router.post("/token")
async def login(db: Annotated[AsyncSession, Depends(get_db)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user = await authenticate_user(db, form_data.username, form_data.password)
    return {
        "access_token": user.username,
        "token_type": "bearer"
    }


@auth_router.get('/read_current_user')
async def read_current_user(user: Users = Depends(oauth2_scheme)):
    return user
