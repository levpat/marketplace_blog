import uvicorn
from fastapi import FastAPI

from config import host, port
from src.users.routers import user_router

app = FastAPI()

app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run('src.main:app',
                host=host,
                port=port,
                reload=True)
