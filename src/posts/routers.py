from fastapi import APIRouter
from starlette.requests import Request

from src.auth.backend import get_current_user
from src.main import app

post_router = APIRouter(prefix='/post', tags=['post'])


