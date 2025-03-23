from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.posts.schemas import CreatePost
from src.posts.backend import pm

post_router = APIRouter(prefix='/posts', tags=['posts'])


@post_router.get("/")
async def posts():
    pass


@post_router.post("/create")
async def create_post(db: Annotated[AsyncSession, Depends(get_db)], post: CreatePost):
    return await pm.create_post(db, post)
