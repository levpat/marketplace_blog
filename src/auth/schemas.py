from pydantic import BaseModel


class AuthSchema(BaseModel):
    username: str
    password: str


class GetAuthDataResponseModel(BaseModel):
    status_code: int
    detail: str
    token: dict