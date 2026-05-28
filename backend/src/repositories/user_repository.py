import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import User


def create(db: Session, user_data: dict[str, Any]) -> User:
    user = User(**user_data)
    db.add(user)
    return user


def get_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalars(stmt).first()
