import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.security import InvalidTokenError, TokenExpiredError, decode_token
from src.db import get_db
from src.db.models.User import User
from src.repositories import user_repository

bearer_scheme = HTTPBearer(auto_error=False)


def _get_raw_token(auth_credentials: HTTPAuthorizationCredentials | None) -> str:
    if auth_credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return auth_credentials.credentials


def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    raw_token = _get_raw_token(auth_credentials)
    try:
        payload = decode_token(
            raw_token, settings.jwt_secret_key, settings.jwt_algorithm
        )
    except (TokenExpiredError, InvalidTokenError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    if payload.get("token_use") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return user
