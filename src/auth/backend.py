from src.config import mail_pass, smtp

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

conf = ConnectionConfig(
    MAIL_USERNAME='auth@testing.com',
    MAIL_PASSWORD=mail_pass,
    MAIL_FROM="info@example.com",
    MAIL_PORT=465,
    MAIL_SERVER=smtp,
    MAIL_FROM_NAME="Company Name",
    MAIL_TLS=False,
    MAIL_SSL=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

