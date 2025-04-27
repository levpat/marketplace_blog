import uuid

from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class UserSchema(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    first_name: str
    last_name: str
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


class CurrentUserSchema(BaseModel):
    id: str
    role: str


class ResponseModelUserSchema(BaseModel):
    status_code: int
    detail: str
    data: list[UserSchema]
