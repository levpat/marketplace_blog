from pydantic import BaseModel


class Post(BaseModel):
    id: str
    title: str
    text: str
    category: str
    image: str


class CreatePost(BaseModel):
    title: str
    text: str
    category: str | None
    image: str | None


class PostPaginator(BaseModel):
    items: list[Post]
    total: int
    offset: int
    limit: int
