from fastapi import Depends, APIRouter, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.backend import create_access_token, authenticate_user, get_current_user, set_token
from src.backend.db_depends import get_session

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post("/login")
async def login(response: Response, db: Annotated[AsyncSession, Depends(get_session)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user = await authenticate_user(db, form_data.username, form_data.password)
    data = {
        "sub": str(user.id),
        "permission": user.is_admin
    }
    token = create_access_token(data)
    set_token(response, token)
    return {
        "status": status.HTTP_201_CREATED,
        "detail": f"Wellcome {user.first_name}!"
    }


@auth_router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {"User": user}


@auth_router.get('/get_admin_user')
async def get_admin(user: Annotated[dict, Depends(get_current_user)]):
    if user.get("permission"):
        return {
            "status": status.HTTP_202_ACCEPTED,
            "detail": "Wellcome Admin!"
        }
    return {
        "status": status.HTTP_401_UNAUTHORIZED,
        "detail": "Need authorization"
    }
