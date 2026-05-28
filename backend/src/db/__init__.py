from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings
from src.db.base import Base
from src.db.models import Account, IdempotencyKey, RefreshToken, User

__all__ = [
    "Account",
    "Base",
    "IdempotencyKey",
    "RefreshToken",
    "User",
    "get_db",
    "init_db",
]

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
