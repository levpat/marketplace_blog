from typing import Annotated
from fastapi import Depends, HTTPException, status
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
        categories = await self.session.scalars(select(Category).order_by(Category.id))
        return GetCategoriesSchema(
            categories=categories.all()
        )

    async def create(self,
                     title: str) -> CategorySchema:
        category = await self.session.scalar(select(Category)
                                             .where(Category.title == title))
        if category is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This category is already exist"
            )
        new_category = Category(title=title)
        self.session.add(new_category)
        await self.session.commit()
        return CategorySchema(
            id=new_category.id,
            title=new_category.title
        )


def get_category_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CategoryRepository:
    return CategoryRepository(session)
