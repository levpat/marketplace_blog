from fastapi import APIRouter, status

from src.auth.backend import send_email
from src.users.schemas import ResponseModelUserSchema, CreateUserSchema
from src.users.service import UserService

user_router = APIRouter(prefix='/users', tags=['users'])


@user_router.post("/", response_model=ResponseModelUserSchema)
async def create(
        user_service: UserService,
        create_user: CreateUserSchema
) -> ResponseModelUserSchema:
    user = await user_service.create(create_user=create_user)
    send_email.delay(create_user.email)
    return ResponseModelUserSchema(
        status_code=status.HTTP_201_CREATED,
        detail="User create",
        data=user
    )
