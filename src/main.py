import uvicorn
from fastapi import FastAPI, HTTPException, status
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send
import jwt

from config import host, port
from src.users.routers import user_router
from src.auth.routers import auth_router
from config import secret, alg


class JWTMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.exclude_paths = {
            "/docs",
            "/openapi.json",
            "/auth/login",
            "/auth/register"
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


app = FastAPI()
app.add_middleware(JWTMiddleware)

app.include_router(user_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run('src.main:app',
                host=host,
                port=port,
                reload=True)
