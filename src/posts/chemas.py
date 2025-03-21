from fastapi import UploadFile
from pydantic import BaseModel


class BasePost(BaseModel):
    title: str
    text: str
    category: str | None


class CreatePost(BasePost):
    image: UploadFile = None  # Optional field for image


class Post(BasePost):
    title: str
    text: str
    category: str | None
    image_url: str | None
