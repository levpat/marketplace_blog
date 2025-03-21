import re

from pydantic import BaseModel, EmailStr, validator

letter_match_pattern = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class CurrentUser(BaseModel):
    id: str
    is_admin: bool | None
