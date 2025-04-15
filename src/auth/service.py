import jwt
from typing import Annotated
from datetime import timedelta, datetime, timezone
from fastapi import status, HTTPException, Depends
from fastapi.responses import Response
from starlette.types import ASGIApp, Scope, Send, Receive
from starlette.requests import Request

from src.auth.schemas import GetAuthDataResponseModel
from src.users.repository import UserRepository, get_user_repository
from src.config import bcrypt_context, access_token_expire_minutes, \
    secret, alg


class AuthService:
    def __init__(self,
                 repository: UserRepository):
        self.repository = repository

    @staticmethod
    def create_access_token(
            data: dict,
            expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret, algorithm=alg)

    @staticmethod
    def set_token(
            response: Response,
            token: str
    ) -> None:
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True
        )

    async def authenticate_user(self,
                                username: str,
                                password: str,
                                response: Response
                                ) -> GetAuthDataResponseModel:
        user = await self.repository.get_user_for_authenticate(username)
        if not user or not bcrypt_context.verify(password, user.hashed_password) or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        data = {
            "clientID": str(user.id),
            "username": user.username,
            "name": user.first_name,
            "email": user.email
        }
        token = self.create_access_token(data)
        self.set_token(response, token)

        return GetAuthDataResponseModel(
            status_code=status.HTTP_200_OK,
            detail=f"Wellcome {user.first_name}!",
            token=token
        )


def get_auth_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(repository)


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
