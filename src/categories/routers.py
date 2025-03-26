from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.categories.schemas import CreateCategory
from src.categories.backend import cm

category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/')
async def get(db: Annotated[AsyncSession, Depends(get_db)]):
    return await cm.get(db)


@category_router.post('/create')
async def post(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory):
    return await cm.create(db, create_category)
