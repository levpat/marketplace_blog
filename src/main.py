import uvicorn
from fastapi import FastAPI

from src.config import get_settings
from src.auth.service import JWTMiddleware
from src.categories.routers import category_router
from src.users.routers import user_router
from src.auth.routers import auth_router
from src.posts.routers import post_router

app = FastAPI()
app.add_middleware(JWTMiddleware, settings=get_settings())

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(category_router)

if __name__ == "__main__":
    uvicorn.run('src.main:app',
                host=get_settings().host,
                port=get_settings().port,
                reload=True)
