from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_session
from src.categories.schemas import CreateCategorySchema, CategorySchema, GetCategoriesSchema
from src.categories.service import get_category_service, CategoryService

category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/', response_model=GetCategoriesSchema, status_code=status.HTTP_200_OK)
async def get(
        category_srvice: Annotated[CategoryService, Depends(get_category_service)]
) -> GetCategoriesSchema:
    return await category_srvice.get()


@category_router.post('/create', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create(
        category_service: Annotated[CategoryService, Depends(get_category_service)],
        create_category: CreateCategorySchema
) -> CategorySchema:
    return await category_service.create(create_category)
