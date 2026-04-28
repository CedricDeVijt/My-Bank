import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    RefreshTokenError,
)
from src.core.security import (
    InvalidTokenError,
    TokenExpiredError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.db.models import User
from src.repositories import refresh_token_repository, user_repository
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


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")
    return user


def issue_token_pair(
    db: Session, user: User, family_id: uuid.UUID | None = None
) -> tuple[str, str]:
    now = datetime.now(UTC).replace(tzinfo=None)
    family = family_id or uuid.uuid4()

    # Create access and refresh token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        secret_key=settings.jwt_secret_key,
        expires_in=settings.jwt_access_token_expires_in,
        algorithm=settings.jwt_algorithm,
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "family_id": str(family)},
        secret_key=settings.jwt_secret_key,
        expires_in=settings.jwt_refresh_token_expires_in,
        algorithm=settings.jwt_algorithm,
    )

    # Save refresh token in db
    refresh_token_repository.create(
        db,
        data={
            "user_id": user.id,
            "token_hash": hash_token(refresh_token),
            "family_id": family,
            "created_at": now,
            "expires_at": now
            + timedelta(seconds=settings.jwt_refresh_token_expires_in),
        },
    )

    db.commit()

    return access_token, refresh_token


def refresh_tokens(db: Session, raw_refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(
            token=raw_refresh_token,
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    except (TokenExpiredError, InvalidTokenError) as exc:
        raise RefreshTokenError(">Invalid refresh token") from exc

    if payload.get("token_use") != "refresh":
        raise RefreshTokenError(">Invalid refresh token")

    record = refresh_token_repository.get_by_hash(db, hash_token(raw_refresh_token))
    if not record:
        raise RefreshTokenError("Refresh token reuse detected")

    now = datetime.now(UTC).replace(tzinfo=None)
    if record.expires_at <= now:
        refresh_token_repository.revoke_family(db, record.family_id, now)
        db.commit()
        raise RefreshTokenError("Invalid refresh token")

    user = user_repository.get_by_id(db, record.user_id)
    if not user:
        raise RefreshTokenError("Invalid refresh token")

    refresh_token_repository.revoke_token(db, record, now)
    access_token, new_refresh_token = issue_token_pair(db, user, record.family_id)
    return access_token, new_refresh_token


def logout(db: Session, user_id: uuid.UUID, raw_refresh_token: str) -> None:
    record = refresh_token_repository.get_by_hash(db, hash_token(raw_refresh_token))

    if not record or record.user_id != user_id:
        raise RefreshTokenError("Invalid refresh token")

    if record.revoked_at is None:
        refresh_token_repository.revoke_token(
            db, record, datetime.now(UTC).replace(tzinfo=None)
        )
        db.commit()
