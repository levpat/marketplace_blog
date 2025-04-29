from fastapi import Depends, APIRouter
from fastapi import Response
from typing import Annotated

from src.auth.schemas import AuthSchema, GetAuthDataResponseModel
from src.auth.service import get_auth_service, AuthService

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post("/login", response_model=GetAuthDataResponseModel)
async def login(
        response: Response,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        auth_data: AuthSchema
) -> GetAuthDataResponseModel:
    return await auth_service.authenticate_user(
        username=auth_data.username,
        password=auth_data.password,
        response=response
    )
