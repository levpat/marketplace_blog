from typing import Annotated, Sequence
from fastapi import HTTPException, status, Depends
from sqlalchemy import select, func, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.associations.models import PostCategories
from src.backend.db_depends import get_session
from src.categories.models import Category
from src.posts.models import Post, DeletedPost


class PostRepository:
    def __init__(self,
                 session: AsyncSession):
        self.session = session

    async def create(self,
                     title: str,
                     text: str,
                     categories: list[str],
                     image_url: str) -> Post:
        current_post = await self.session.scalar(
            select(Post)
            .where(or_(
                Post.title == title,
                Post.text == text
            )))

        if current_post is None:

            if isinstance(categories, list) and len(categories) == 1:
                categories = categories[0].split(',')

            existing_categories = await self.session.scalars(select(Category).where(Category.title.in_(categories)))
            existing_categories = existing_categories.all()

            if len(existing_categories) != len(categories):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Some categories not found"
                )

            post = Post(title=title,
                        text=text,
                        image_url=image_url)
            self.session.add(post)
            await self.session.flush()

            category_ids = [category.id for category in existing_categories]
            post_categories_links = [
                PostCategories(
                    post_id=post.id,
                    category_id=category_id
                ) for category_id in category_ids
            ]

            self.session.add_all(post_categories_links)
            await self.session.commit()

            return post

        if current_post.title == title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with same title is already exist"
            )

        if current_post.text == text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with same text is already exist"
            )

    async def get(self,
                  page: int,
                  page_size: int,
                  categories: list[str],
                  search: str | None
                  ) -> Sequence[Post]:
        if categories is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need to add categories"
            )

        if isinstance(categories, list) and len(categories) == 1:
            categories = categories[0].split(',')

        existing_categories = await self.session.scalars(select(Category).where(Category.title.in_(categories)))
        existing_categories = existing_categories.all()

        if len(categories) != len(existing_categories):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some categories not found"
            )

        category_ids = [category.id for category in existing_categories]

        query = select(Post).distinct(Post.title)

        if search:
            columns = func.coalesce(Post.title, '').concat(func.coalesce(Post.text, ''))
            columns = columns.self_group()
            query = query.where(
                columns.bool_op('%')(search)
            ).order_by(
                Post.title,
                func.similarity(columns, search).desc()
            )
        if category_ids:
            query = (
                query
                .join(Post.category)
                .where(Category.id.in_(category_ids))
                .options(selectinload(Post.category))
            )

        query = query.limit(page_size).offset((page - 1) * page_size)

        posts = await self.session.scalars(query)
        return posts.all()

    async def update(self,
                     post_id: str,
                     title: str,
                     text: str,
                     categories: list[str],
                     image_url: str) -> list[Post]:
        post_for_update = await self.session.scalar(select(Post).where(post_id == Post.id))

        if post_for_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if isinstance(categories, list) and len(categories) == 1:
            categories = categories[0].split(',')

        existing_categories = await self.session.scalars(select(Category).where(Category.title.in_(categories)))
        existing_categories = existing_categories.all()

        if len(existing_categories) != len(categories):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some categories not found"
            )

        if post_for_update.title == title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with same title is already exist"
            )

        if post_for_update.text == text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with same text is already exist"
            )

        else:
            post_for_update.title = title
            post_for_update.text = text
            post_for_update.image_url = image_url

            self.session.add(post_for_update)
            await self.session.flush()

            await self.session.execute(
                delete(PostCategories)
                .where(post_id == PostCategories.post_id)
            )

            category_ids = [category.id for category in existing_categories]
            post_categories_links = [
                PostCategories(
                    post_id=post_for_update.id,
                    category_id=category_id
                ) for category_id in category_ids
            ]

            self.session.add_all(post_categories_links)
            await self.session.commit()

            return [post_for_update]

    async def delete(self, post_id: str) -> list[DeletedPost]:

        post_for_delete = await self.session.scalar(select(Post).where(post_id == Post.id))

        if post_for_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        await self.session.execute(
            delete(PostCategories)
            .where(post_id == PostCategories.post_id)
        )

        await self.session.execute(delete(Post).where(post_id == Post.id))

        deleted_post = DeletedPost(
            id=post_for_delete.id,
            title=post_for_delete.title,
            text=post_for_delete.text,
            image_url=post_for_delete.image_url,
            created_at=post_for_delete.created_at)

        self.session.add(deleted_post)
        await self.session.commit()
        return [deleted_post]


def get_post_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> PostRepository:
    return PostRepository(session)
