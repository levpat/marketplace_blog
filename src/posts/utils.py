from typing import BinaryIO, Annotated
from minio import Minio
from fastapi import Depends

from src.config import get_settings, Settings


class MinioHandler:
    def __init__(self,
                 minio_endpoint: str,
                 access_key: str,
                 secret_key: str,
                 bucket: str,
                 secure: bool = False):
        self.client = Minio(
            minio_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket = bucket

    def upload_file(self, name: str, file: BinaryIO, length: int):
        return self.client.put_object(self.bucket, name, file, length=length)

    def list(self):
        objects = list(self.client.list_objects(self.bucket))
        return [{"name": i.object_name, "last_modified": i.last_modified} for i in objects]


def get_minio_handler(
        settings: Annotated[Settings, Depends(get_settings)]
) -> MinioHandler:
    return MinioHandler(
        settings.minio_url,
        settings.minio_access,
        settings.minio_secret,
        settings.minio_bucket,
        False
    )
