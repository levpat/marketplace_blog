from io import BytesIO
from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db_depends import get_db
from src.posts.schemas import Post, CreatePost
from src.posts.backend import pm
from src.posts.utils import MinioHandler
from src.config import minio_bucket, minio_secret, minio_url, minio_access

post_router = APIRouter(prefix='/posts', tags=['posts'])

minio_handler = MinioHandler(
    minio_url,
    minio_access,
    minio_secret,
    minio_bucket,
    False
)


@post_router.get("/posts", response_model=List[Post])
# @pagination
async def get(db: Annotated[AsyncSession, Depends(get_db)],
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              category: int | None = Query(default=None),
              search: str | None = Query(default=None)):
    return await pm.get(db=db, limit=limit, offset=offset, category=category, search=search)


@post_router.post("/create")
async def create_post(db: Annotated[AsyncSession, Depends(get_db)], post: CreatePost):
    return await pm.create(db, post)


@post_router.get("/all")
async def get_all(db: Annotated[AsyncSession, Depends(get_db)]):
    return await pm.get_all(db)


@post_router.post('/s3/upload/test')
async def upload(file: UploadFile = File(...)):
    try:
        file_contents = await file.read()

        file_stream = BytesIO(file_contents)

        minio_handler.upload_file(file.filename, file_stream, len(file_contents))

        return {
            "status": "uploaded",
            "name": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@post_router.get('/s3/list')
async def list_files():
    return minio_handler.list()
