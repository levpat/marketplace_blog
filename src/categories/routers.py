from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.categories.schemas import CreateCategorySchema, CategorySchema, GetCategoriesSchema
from src.categories.service import get_category_service, CategoryService

category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/', response_model=GetCategoriesSchema, status_code=status.HTTP_200_OK)
async def get(
        category_service: Annotated[CategoryService, Depends(get_category_service)]
) -> GetCategoriesSchema:
    return await category_service.get()


@category_router.post('/create', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create(
        category_service: Annotated[CategoryService, Depends(get_category_service)],
        create_category: CreateCategorySchema = Depends()
) -> CategorySchema:
    return await category_service.create(create_category)
