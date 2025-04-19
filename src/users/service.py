import asyncio
from typing import Annotated

from celery import Celery
from fastapi import Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from starlette import status

from src.users.models import Users
from src.users.repository import UserRepository, get_user_repository
from src.users.schemas import CreateUserSchema
from src.config import get_settings, Settings


class UserService:
    def __init__(self,
                 repository: UserRepository,
                 settings: Settings):
        self.repository = repository
        self.settings = settings

    async def create(self,
                     create_user: CreateUserSchema
                     ) -> list[Users]:
        user = await self.repository.create(first_name=create_user.first_name,
                                            last_name=create_user.last_name,
                                            username=create_user.username,
                                            email=str(create_user.email),
                                            password=self.settings.bcrypt_context.hash(create_user.password))

        return user


def get_user_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)],
        settings: Annotated[Settings, Depends(get_settings)]
) -> UserService:
    return UserService(
        repository=repository,
        settings=settings
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
            "status_code": status.HTTP_200_OK,
            "detail": "Success"
        }


def get_email_service(
        settings: Annotated[Settings, Depends(get_settings)]
) -> EmailService:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.mail_address_2,
        MAIL_PASSWORD=settings.mail_pass_for_google,
        MAIL_PORT=587,
        MAIL_SERVER=settings.smtp_google,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        MAIL_FROM=settings.mail_address_2,
    )
    return EmailService(conf)


celery = Celery(
    __name__,
    broker=get_settings().broker,
    backend=get_settings().backend,
    broker_connection_retry_on_startup=True
)


@celery.task()
def send_email(
        email_service: Annotated[EmailService, Depends(get_email_service)],
        email: EmailStr | str
) -> dict:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(email_service.send_mail(email))
    loop.close()
    return result
