from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.posts.schemas import Post, CreatePost, DeletedPost
from src.posts.backend import pm

post_router = APIRouter(prefix='/posts', tags=['posts'])


@post_router.get("/posts", response_model=List[Post])
# @pagination
async def get(db: Annotated[AsyncSession, Depends(get_db)],
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              category: int | None = Query(default=None),
              search: str | None = Query(default=None)):
    return await pm.get(db=db, limit=limit, offset=offset, category=category, search=search)


@post_router.post("/create")
async def create_post(db: Annotated[AsyncSession, Depends(get_db)], post: CreatePost = Depends()):
    return await pm.create(db, post)


@post_router.put("/{post_id}")
async def update(
        db: Annotated[AsyncSession, Depends(get_db)],
        post_id: str,
        update_post_model: CreatePost = Depends()
):
    return await pm.update(db, post_id, update_post_model)


@post_router.delete("/{post_id}")
async def delete(
        db: Annotated[AsyncSession, Depends(get_db)],
        post_id: str
):
    await pm.delete(db, post_id)
