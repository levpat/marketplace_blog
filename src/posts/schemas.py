import uuid
from datetime import datetime
from typing import Sequence

from fastapi import UploadFile, Form
from pydantic import BaseModel


class BasePostSchema(BaseModel):
    title: str
    image_url: str | None


class CreatePostSchema(BasePostSchema):
    text: str
    categories: list[str]
    image: UploadFile = Form()


class PostSchema(BasePostSchema):
    id: uuid.UUID = uuid.uuid4()
    text: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class GetPostSchema(BaseModel):
    data: Sequence[PostSchema]


class DeletedPostSchema(PostSchema):
    deleted_at: datetime


class ResponseModelPostSchema(GetPostSchema):
    status_code: int
    detail: str
    data: list[PostSchema]
