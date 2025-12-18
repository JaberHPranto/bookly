from pathlib import Path
from typing import List

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)

from src.config import Config

BASE_DIR = Path(__file__).resolve().parent


mail_conf = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail = FastMail(mail_conf)


def create_message(subject: str, recipients: List[str], body: str):
    message: MessageSchema = MessageSchema(
        subject=subject,
        recipients=[NameEmail(name="", email=email) for email in recipients],
        body=body,
        subtype=MessageType.html,
    )

    return message
