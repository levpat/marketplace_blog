import asyncio
from typing import Annotated

import jwt
from datetime import datetime, timezone, timedelta
from celery import Celery
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from src.backend.db_depends import get_session

from src.config import (
    mail_pass_for_google, smtp_google, mail_address_2,
    secret, alg)
from src.users.models import Users

ACCESS_TOKEN_EXPIRE_MINUTES = 20

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

celery = Celery(
    __name__,
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True
)

conf = ConnectionConfig(
    MAIL_USERNAME=mail_address_2,
    MAIL_PASSWORD=mail_pass_for_google,
    MAIL_PORT=587,
    MAIL_SERVER=smtp_google,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM=mail_address_2,
)


async def _send_email(email: EmailStr | str) -> dict:
    message = MessageSchema(
        recipients=[email],
        subject="Test sending email",
        body='Благодарим Вас за регистрацию!',
        charset="utf-8",
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return {
        'status_code': status.HTTP_201_CREATED,
        'transactions': 'Success'
    }


@celery.task()
def send_email(email: EmailStr | str) -> dict:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_send_email(email))
    loop.close()
    return result


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_session)],
                            username: str, password: str):
    user = await db.scalar(select(Users).where(Users.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Need authorization"
        )

    try:
        payload = jwt.decode(token, secret, algorithms=[alg])
        user_id: str | None = payload.get("sub")
        is_admin: str | None = payload.get("permission")
        expire: int | None = payload.get("exp")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )

        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token denied"
            )

        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token format"
            )

        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired!"
            )

        return {
            "sub": user_id,
            "permission": is_admin
        }


    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm=alg)


def set_token(response: Response, token: str) -> None:
    response.set_cookie(key="access_token", value=token, httponly=True)


class JWTMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.exclude_paths = {
            "/docs",
            "/openapi.json",
            "/auth/login",
            "/users/",
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("root_path", "") + scope.get("path", "")

        if path in self.exclude_paths:
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        token = request.cookies.get("access_token")

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Need authorization"
            )

        try:
            payload = jwt.decode(token, secret, algorithms=[alg])
            scope["user"] = payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT token"
            )

        await self.app(scope, receive, send)
