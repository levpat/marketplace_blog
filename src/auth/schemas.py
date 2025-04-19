from pydantic import BaseModel


class GetAuthDataResponseModel(BaseModel):
    status_code: int
    detail: str
    token: dict