from typing import Annotated
from fastapi import HTTPException, status, Depends
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_session
from src.posts.models import Post, DeletedPost


class PostRepository:
    def __init__(self,
                 session: AsyncSession):
        self.session = session

    async def create(self,
                     title: str,
                     text: str,
                     category_id: int | None,
                     image_url: str | None) -> Post:
        post = Post(title=title,
                    text=text,
                    category_id=category_id,
                    image_url=image_url)
        self.session.add(post)
        await self.session.commit()

        return post

    async def get(self,
                  page: int,
                  page_size: int,
                  category: int | None,
                  search: str | None
                  ) -> list[Post]:
        if search is None:
            result = await self.session.scalars(select(Post).where(category == Post.category_id)
                                                .limit(page_size).offset((page - 1) * page_size))
        else:
            columns = func.coalesce(Post.title, '').concat(func.coalesce(Post.text, '')).self_group()
            columns = columns.self_group()

            res = await self.session.execute(
                select(Post, func.similarity(columns, search), )
                .where(columns.bool_op('%')(search), category == Post.category_id, )
                .order_by(func.similarity(columns, search).desc(), ).limit(page_size).offset((page - 1) * page_size)
            )

            result = res.scalars()
        posts = result.all()
        return posts

    async def update(self,
                     post_id: str,
                     title: str,
                     text: str,
                     category_id: int | None,
                     image_url: str | None) -> list[Post]:
        post_for_update = await self.session.scalar(select(Post).where(post_id == Post.id))

        if post_for_update is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post not found"
            )

        post_for_update.title = title
        post_for_update.text = text
        post_for_update.category_id = category_id
        post_for_update.image_url = image_url

        await self.session.commit()

        return [post_for_update]

    async def delete(self, post_id: str) -> list[DeletedPost]:
        post_for_delete = await self.session.scalar(select(Post).where(post_id == Post.id))
        if post_for_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        await self.session.execute(delete(Post).where(post_id == Post.id))

        deleted_post = DeletedPost(
            id=post_for_delete.id,
            title=post_for_delete.title,
            text=post_for_delete.text,
            category_id=post_for_delete.category_id,
            image_url=post_for_delete.image_url,
            created_at=post_for_delete.created_at)

        self.session.add(deleted_post)
        await self.session.commit()
        return [deleted_post]


def get_post_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> PostRepository:
    return PostRepository(session)
