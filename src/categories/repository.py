from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.categories.schemas import CategorySchema, GetCategoriesSchema
from src.backend.db_depends import get_session


class CategoryRepository:
    def __init__(self,
                 session: AsyncSession):
        self.session = session

    async def get(self) -> GetCategoriesSchema:
        categories = await self.session.scalars(select(Category).order_by(Category.id)).all()
        return GetCategoriesSchema(
            categories=categories
        )

    async def create(self,
                     title: str) -> CategorySchema:
        category = Category(title=title)
        self.session.add(category)
        await self.session.commit()
        return CategorySchema(
            id=category.id,
            title=category.title
        )


def get_category_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CategoryRepository:
    return CategoryRepository(session)
