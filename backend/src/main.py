from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.accounts import router as account_router
from src.api.v1.auth import router as auth_router
from src.api.v1.transactions import router as transactions_router
from src.api.v1.users import router as users_router
from src.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(account_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

app.include_router(transactions_router, prefix="/api/v1")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    cast(Any, CORSMiddleware),
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
