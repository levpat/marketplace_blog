from src.config import mail_pass, smtp

from fastapi import BackgroundTasks, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME='lion.patskevich@yandex.ru',
    MAIL_PASSWORD=mail_pass,
    MAIL_PORT=465,
    MAIL_SERVER=smtp,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM="lion.patskevich@yandex.ru",
)


async def send_email(email: EmailStr | str) -> dict:
    message = MessageSchema(
        recipients=[email],
        subject="Test sending email",
        body='Благодарим Вас за регистрацию!',
        charset="utf-8",
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return {
        'status_code': status.HTTP_201_CREATED,
        'transactions': 'Success'
    }
