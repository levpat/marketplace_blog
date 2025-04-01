from fastapi import Form
from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    first_name: str = Form()
    last_name: str = Form()
    username: str = Form()
    email: EmailStr = Form()
    password: str = Form()


class CurrentUser(BaseModel):
    id: str
    is_admin: bool | None
