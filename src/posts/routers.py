from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, UploadFile, Form, File

from src.posts.schemas import GetPostSchema, ResponseModelPostSchema, CreatePostSchema, \
    ResponseModelDeletedPostSchema
from src.posts.service import PostService, get_post_service

post_router = APIRouter(prefix='/posts', tags=['posts'])


@post_router.get("/", response_model=GetPostSchema)
async def get(
        post_service: Annotated[PostService, Depends(get_post_service)],
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        categories: list[str] = Query(default=None),
        search: str | None = Query(default=None)
) -> GetPostSchema:
    return await post_service.get(page=page,
                                  page_size=page_size,
                                  categories=categories,
                                  search=search)


@post_router.post(
    "/",
    response_model=ResponseModelPostSchema,
    status_code=status.HTTP_201_CREATED
)
async def create(
        post_service: Annotated[PostService, Depends(get_post_service)],
        image: UploadFile = File(...),
        title: str = Form(...),
        text: str = Form(...),
        categories: list[str] = Form(...)
) -> ResponseModelPostSchema:
    create_post = CreatePostSchema(
        title=title,
        text=text,
        categories=categories,
        image=image
    )
    return await post_service.create(create_post=create_post)


@post_router.put(
    "/",
    response_model=ResponseModelPostSchema,
    status_code=status.HTTP_201_CREATED
)
async def update(
        post_service: Annotated[PostService, Depends(get_post_service)],
        post_id: str = Form(...),
        image: UploadFile = File(...),
        title: str = Form(...),
        text: str = Form(...),
        categories: list[str] = Form(...)
) -> ResponseModelPostSchema:
    updated_post = CreatePostSchema(
        title=title,
        text=text,
        categories=categories,
        image=image
    )
    return await post_service.update(
        post_id=post_id,
        update_post=updated_post
    )


@post_router.delete(
    "/",
    response_model=ResponseModelPostSchema
)
async def delete(
        post_service: Annotated[PostService, Depends(get_post_service)],
        post_id: str
) -> ResponseModelDeletedPostSchema:
    return await post_service.delete(post_id=post_id)
