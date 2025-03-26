import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CreatePost(BaseModel):
    title: str
    text: str
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class Post(CreatePost):
    id: uuid.UUID = uuid.uuid4()
    title: str
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
