from pydantic import BaseModel
from fastapi import Form


class CreateCategorySchema(BaseModel):
    title: str = Form()


class CategorySchema(CreateCategorySchema):
    id: int

    class Config:
        from_attributes = True


class GetCategoriesSchema(BaseModel):
    categories: list[CategorySchema]
