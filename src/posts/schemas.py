import uuid
from datetime import datetime
from typing import Sequence

from fastapi import UploadFile, File
from pydantic import BaseModel


class BasePostSchema(BaseModel):
    title: str
    text: str


class CreatePostSchema(BasePostSchema):
    categories: list[str]
    image: UploadFile = File()


class PostSchema(BasePostSchema):
    id: uuid.UUID = uuid.uuid4()
    image_url: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class DeletedPostSchema(BasePostSchema):
    id: uuid.UUID = uuid.uuid4()
    image_url: str
    created_at: datetime
    deleted_at: datetime

    class Config:
        from_attributes = True


class GetPostSchema(BaseModel):
    data: Sequence[PostSchema]


class ResponseModelPostSchema(GetPostSchema):
    status_code: int
    detail: str
    data: list[PostSchema]


class ResponseModelDeletedPostSchema(
    ResponseModelPostSchema
):
    data: list[DeletedPostSchema]
