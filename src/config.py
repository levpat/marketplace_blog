from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    db_url: str
    host: str
    port: int
    secret_key: str
    alg: str
    mail_address_for_google: str
    mail_pass_for_google: str
    smtp_2: str
    minio_access_key: str
    minio_secret_key: str
    minio_url: str
    minio_bucket: str
    broker: str
    backend: str
    valid_exceptions: tuple = {'.png', '.jpg', '.jpeg', '.pdf'}
    access_token_expire_minutes: int = 20
    bcrypt_context: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')

    model_config = SettingsConfigDict(
        env_file="../.env"
    )


@lru_cache
def get_settings():
    return Settings()
