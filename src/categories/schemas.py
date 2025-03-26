from pydantic import BaseModel


class Category(BaseModel):
    id: str
    title: str


class CreateCategory(BaseModel):
    title: str