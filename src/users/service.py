from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from faststream.redis import RedisBroker
from pydantic import EmailStr
from contextlib import asynccontextmanager

from src.users.models import Users
from src.users.repository import UserRepository, get_user_repository
from src.users.schemas import CreateUserSchema
from src.config import bcrypt_context, redis_url, pass_yandex, mail_yandex, smtp_ya

broker = RedisBroker(redis_url)


class UserService:
    def __init__(self,
                 repository: UserRepository):
        self.repository = repository

    async def create(self,
                     create_user: CreateUserSchema
                     ) -> list[Users]:
        user = await self.repository.create(first_name=create_user.first_name,
                                            last_name=create_user.last_name,
                                            username=create_user.username,
                                            email=str(create_user.email),
                                            password=bcrypt_context.hash(create_user.password))

        return user


def get_user_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(
        repository=repository
    )


class EmailService:
    def __init__(self,
                 conf: ConnectionConfig):
        self.conf = conf
        self.fm = FastMail(conf)

    async def send_mail(self,
                        email: EmailStr | str) -> dict:
        message = MessageSchema(
            recipients=[email],
            subject="Test sending email",
            body="Благодарим Вас за регистрацию!",
            charset="utf-8",
            subtype=MessageType.plain
        )
        await self.fm.send_message(message)
        return {
            "detail": "Success"
        }


@broker.subscriber("email_channel")
async def handle_email_task(
        email: str
) -> None:
    conf = ConnectionConfig(
        MAIL_USERNAME=mail_yandex,
        MAIL_PASSWORD=pass_yandex,
        MAIL_PORT=465,
        MAIL_SERVER=smtp_ya,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        MAIL_FROM=mail_yandex,
    )
    email_service = EmailService(conf)
    await email_service.send_mail(email)
