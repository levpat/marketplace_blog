from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Set


class Settings(BaseSettings):
    # Database
    db_url: str
    test_db_url: str
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    secret_key: str
    alg: str
    access_token_expire_minutes: int = 20
    bcrypt_context: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')

    # Email
    mail_address: str
    yandex_pass: str
    smtp: str

    # MinIO
    minio_access_key: str
    minio_secret_key: str
    minio_url: str
    minio_bucket: str

    # Redis
    broker: str

    # File validation
    valid_exceptions: Set[str] = {'.png', '.jpg', '.jpeg', '.pdf'}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
        case_sensitive=False,
        validate_assignment=True
    )


@lru_cache
def get_settings():
    return Settings()
