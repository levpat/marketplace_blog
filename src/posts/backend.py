from typing import Annotated

from fastapi import HTTPException, status, Depends

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.posts.models import Post


class PostManager:

    @staticmethod
    async def create(db, create_post):
        try:
            await db.execute(insert(Post).values(
                title=create_post.title,
                text=create_post.text,
                category=create_post.category,
                image_url=create_post.image
            ))

            await db.commit()

        except Exception as error:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during creating post: {str(error)}"

            )

        return {
            "status_code": status.HTTP_201_CREATED,
            "transaction": "Success"
        }

    @staticmethod
    async def get(db: Annotated[AsyncSession, Depends(get_db)], limit: int, offset: int):
        try:
            result = await db.scalars(select(Post).order_by(Post.id).limit(limit).offset(offset))
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
