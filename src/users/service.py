from typing import Annotated

from fastapi import Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from faststream.redis import RedisBroker
from pydantic import EmailStr

from src.users.models import Users
from src.users.repository import UserRepository, get_user_repository
from src.users.schemas import CreateUserSchema
from src.settings.config import get_settings

broker = RedisBroker(get_settings().broker)




class UserService:
    def __init__(self,
                 repository: UserRepository):
        self.repository = repository
        self.settings = get_settings()

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
        MAIL_USERNAME=get_settings().mail_address,
        MAIL_PASSWORD=get_settings().yandex_pass,
        MAIL_PORT=465,
        MAIL_SERVER=get_settings().smtp,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        MAIL_FROM=get_settings().mail_address,
    )
    email_service = EmailService(conf)
    await email_service.send_mail(email)
