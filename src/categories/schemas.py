from pydantic import BaseModel


class CreateCategorySchema(BaseModel):
    title: str




class CategorySchema(CreateCategorySchema):
    id: int

    class Config:
        from_attributes = True


class GetCategoriesSchema(BaseModel):
    categories: list[CategorySchema]
