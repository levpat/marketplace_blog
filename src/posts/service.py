import os
from io import BytesIO
from typing import Annotated

from fastapi import UploadFile, HTTPException, status, Depends

from src.posts.repository import PostRepository, get_post_repository
from src.posts.schemas import CreatePostSchema, ResponseModelPostSchema, GetPostSchema
from src.posts.utils import MinioHandler, get_minio_handler
from src.config import minio_bucket, minio_url, valid_exceptions


class PostService:
    def __init__(self,
                 repository: PostRepository,
                 client: MinioHandler):
        self.repository = repository
        self.client = client

    async def get_upload_image_url(self,
                                   file: UploadFile) -> str:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in valid_exceptions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid file type. Only .png, .jpg, .jpeg and .pdf are allowed'
            )
        max_file_size = 10 * 1024 * 1024  # 10 МБ
        if file.size > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='File size exceeds the limit (10 MB)'
            )
        file_name = file.filename

        file_contents = await file.read()
        file_stream = BytesIO(file_contents)
        self.client.upload_file(file_name, file_stream, len(file_contents))

        url = f'http://{minio_url}/{minio_bucket}/{file.filename}'
        return url

    async def get(self,
                  page: int,
                  page_size: int,
                  category: int | None,
                  search: str | None) -> GetPostSchema:
        posts = await self.repository.get(page=page,
                                          page_size=page_size,
                                          category=category,
                                          search=search)
        return GetPostSchema(
            posts=posts
        )

    async def create(self,
                     create_post: CreatePostSchema
                     ) -> ResponseModelPostSchema:
        post = await self.repository.create(title=create_post.title,
                                            text=create_post.text,
                                            category_id=create_post.category.id,
                                            image_url=await self.get_upload_image_url(create_post.image)
                                            )
        return ResponseModelPostSchema(
            status_code=status.HTTP_201_CREATED,
            detail="Post created",
            data=[post]
        )

    async def update(
            self,
            post_id: str,
            update_post: CreatePostSchema
    ) -> ResponseModelPostSchema:
        updated_post = await self.repository.update(
            post_id=post_id,
            title=update_post.title,
            text=update_post.text,
            category_id=update_post.category_id,
            image_url=await self.get_upload_image_url(update_post.image)
        )
        return ResponseModelPostSchema(
            status_code=status.HTTP_201_CREATED,
            detail="Post updated",
            data=updated_post
        )

    async def delete(
            self,
            post_id: str
    ) -> ResponseModelPostSchema:
        post = await self.repository.delete(post_id=post_id)
        return ResponseModelPostSchema(
            status_code=status.HTTP_200_OK,
            detail="Post delete",
            data=[post]
        )


def get_post_service(
        repository: Annotated[PostRepository, Depends(get_post_repository)],
        client: Annotated[MinioHandler, Depends(get_minio_handler)]
) -> PostService:
    return PostService(repository, client)
