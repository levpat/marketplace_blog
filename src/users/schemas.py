import uuid

from fastapi import Form
from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    first_name: str = Form()
    last_name: str = Form()
    username: str = Form()
    email: EmailStr = Form()
    password: str = Form()


class UserSchema(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    first_name: str
    last_name: str
    username: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True


class CurrentUserSchema(BaseModel):
    id: str
    is_admin: bool | None


class ResponseModelUserSchema(BaseModel):
    status_code: int
    detail: str
    data: list
