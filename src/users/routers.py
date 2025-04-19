from typing import Annotated
from fastapi import APIRouter, status, Depends

from src.users.schemas import ResponseModelUserSchema, CreateUserSchema
from src.users.service import UserService, get_user_service, broker

user_router = APIRouter(prefix='/users', tags=['users'])


@user_router.post("/", response_model=ResponseModelUserSchema)
async def create(
        user_service: Annotated[UserService, Depends(get_user_service)],
        create_user: Annotated[CreateUserSchema, Depends()]
) -> ResponseModelUserSchema:
    user = await user_service.create(create_user=create_user)

    await broker.publish(
        message=create_user.email,
        channel="email_channel"
    )

    return ResponseModelUserSchema(
        status_code=status.HTTP_201_CREATED,
        detail="User create",
        data=user
    )
