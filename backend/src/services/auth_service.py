from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.core.exceptions import EmailAlreadyRegisteredError
from src.core.security import hash_password
from src.db.models import User
from src.repositories import user_repository
from src.schemas.User import UserCreate


def register_user(db: Session, payload: UserCreate) -> User:
    # check if email is already used
    if user_repository.get_by_email(db=db, email=payload.email):
        raise EmailAlreadyRegisteredError("Email already registered")

    # Create the user
    user_data = payload.model_dump(exclude={"password"})
    user_data["hashed_password"] = hash_password(payload.password)
    user = user_repository.create(db, user_data)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyRegisteredError("Email already registered") from exc
    db.refresh(user)

    return user
