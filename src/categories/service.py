from typing import Annotated
from fastapi import Depends

from src.categories.repository import CategoryRepository, get_category_repository
from src.categories.schemas import CategorySchema, CreateCategorySchema, GetCategoriesSchema


class CategoryService:
    def __init__(self,
                 repository: CategoryRepository):
        self.repository = repository

    async def create(self, create_category: CreateCategorySchema) -> CategorySchema:
        return await self.repository.create(create_category.title)

    async def get(self) -> GetCategoriesSchema:
        return await self.repository.get()


def get_category_service(
        repository: Annotated[CategoryRepository, Depends(get_category_repository)]
) -> CategoryService:
    return CategoryService(repository)
