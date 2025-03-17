import uvicorn
from fastapi import FastAPI

from config import host, port
from src.users.routers import user_router
from src.auth.routers import auth_router

app = FastAPI()

app.include_router(user_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run('src.main:app',
                host=host,
                port=port,
                reload=True)
