from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.categories.models import Category
from src.categories.schemas import CreateCategory


class CategoryManager:
    @staticmethod
    async def create(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory):
        try:
            await db.execute(insert(Category).values(title=create_category.title))
            await db.commit()
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            )

        return {
            "status_code": status.HTTP_201_CREATED,
            "detail": "Category created!"
        }

    @staticmethod
    async def get(db: Annotated[AsyncSession, Depends(get_db)]):
        try:
            result = await db.scalars(select(Category).order_by(Category.id))
            return result.all()
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )


cm = CategoryManager
