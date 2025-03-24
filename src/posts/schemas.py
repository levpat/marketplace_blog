import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Post(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    title: str
    text: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class CreatePost(Post):
    title: str
    text: str
    category: Optional[str] = None
    image_url: Optional[str] = None
