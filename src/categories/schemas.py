from pydantic import BaseModel


class CreateCategory(BaseModel):
    title: str


class Category(CreateCategory):
    title: str
    id: int
