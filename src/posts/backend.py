from typing import Annotated

from fastapi import HTTPException, status, Depends

from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.posts.models import Post
from src.categories.models import Category


class PostManager:

    @staticmethod
    async def create(db, create_post):
        try:
            category = await db.scalar(select(Category).where(Category.id == create_post.category_id))
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='There is no category found'
                )

            await db.execute(insert(Post).values(
                title=create_post.title,
                text=create_post.text,
                category_id=create_post.category_id,
                image_url=create_post.image_url
            ))

            await db.commit()

            return {
                "status_code": status.HTTP_201_CREATED,
                "transaction": "Success",
            }

        except Exception as error:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during creating post: {str(error)}"
            )

    @staticmethod
    async def get(
            db: Annotated[AsyncSession, Depends(get_db)],
            limit: int,
            offset: int,
            category: int | None = None,
            search: str | None = None
    ):
        try:
            if search is None:
                result = await db.scalars(select(Post).where(Post.category_id == category)
                                          .limit(limit).offset(offset))

            else:
                columns = func.coalesce(Post.title, '').concat(func.coalesce(Post.text, '')).self_group()
                columns = columns.self_group()

                res = await db.execute(
                    select(Post, func.similarity(columns, search), )
                    .where(columns.bool_op('%')(search), Post.category_id == category, )
                    .order_by(func.similarity(columns, search).desc(), ).limit(limit).offset(offset)
                )
                result = res.scalars()
            return result.all()

        except Exception as error:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during fetching post: {str(error)}"

            )

    @staticmethod
    async def get_all(db: Annotated[AsyncSession, Depends(get_db)]):
        result = await db.scalars(select(Post).order_by(Post.created_at))
        return result.all()


pm = PostManager
