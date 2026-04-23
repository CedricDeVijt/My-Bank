from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api.v1.auth import router as auth_router
from src.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}
