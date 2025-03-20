import asyncio
from celery import shared_task
from fastapi import status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.config import mail_pass, smtp, mail_address, mail_pass_for_google, smtp_google, mail_address_2

conf = ConnectionConfig(
    MAIL_USERNAME=mail_address_2,
    MAIL_PASSWORD=mail_pass_for_google,
    MAIL_PORT=587,
    MAIL_SERVER=smtp_google,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM=mail_address_2,
)


async def _send_email(email: EmailStr | str) -> dict:
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


@shared_task()
def send_email(email: EmailStr | str) -> dict:
    asyncio.run(_send_email(email))
    return {
        "task": "email sending"
    }
