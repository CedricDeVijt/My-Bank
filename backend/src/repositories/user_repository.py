from sqlalchemy.orm import Session
from src.db.models import User


def create(db: Session, user_data: dict):
    user = User(**user_data)
    db.add(user)
    return user


def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()
