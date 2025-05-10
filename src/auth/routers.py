from fastapi import Depends, APIRouter
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.auth.schemas import GetAuthDataResponseModel
from src.auth.service import get_auth_service, AuthService

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post("/login", response_model=GetAuthDataResponseModel)
async def login(
        response: Response,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> GetAuthDataResponseModel:
    return await auth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password,
        response=response
    )
