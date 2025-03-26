from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.posts.schemas import Post, CreatePost
from src.posts.backend import pm

post_router = APIRouter(prefix='/posts', tags=['posts'])


@post_router.get("/posts", response_model=List[Post])
# @pagination
async def get(db: Annotated[AsyncSession, Depends(get_db)],
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              category: int | None = Query(default=None)):
    return await pm.get(db=db, limit=limit, offset=offset, category=category)


@post_router.post("/create")
async def create_post(db: Annotated[AsyncSession, Depends(get_db)], post: CreatePost):
    return await pm.create(db, post)


@post_router.get("/all")
async def get_all(db: Annotated[AsyncSession, Depends(get_db)]):
    return await pm.get_all(db)
