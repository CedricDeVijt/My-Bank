from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.core.config import settings
from src.core.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    RefreshTokenError,
)
from src.core.idempotency import idempotent
from src.db import get_db
from src.db.models import User
from src.schemas.Token import LogoutRequest, RefreshTokenRequest, TokenResponse
from src.schemas.User import UserCreate, UserLogin, UserResponse
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _build_token_response(access_token: str, refresh_token: str) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires_in=settings.jwt_access_token_expires_in,
        refresh_token_expires_in=settings.jwt_refresh_token_expires_in,
    )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@idempotent(ttl_seconds=3600)
def register_user(
    user: UserCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    try:
        created = auth_service.register_user(payload=user, db=db)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    return UserResponse(
        first_name=created.first_name, last_name=created.last_name, email=created.email
    )


@router.post("/login", response_model=TokenResponse)
@idempotent(ttl_seconds=3600)
def login_user(
    credentials: UserLogin,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    # authenticate user
    try:
        user = auth_service.authenticate_user(
            db, credentials.email, credentials.password
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # issue the tokens
    access_token, refresh_token = auth_service.issue_token_pair(db, user)
    return _build_token_response(access_token, refresh_token)


@router.post("/token/refresh", response_model=TokenResponse)
@idempotent(ttl_seconds=3600)
def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    try:
        access_token, refresh_token = auth_service.refresh_tokens(
            db, payload.refresh_token
        )
    except RefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return _build_token_response(access_token, refresh_token)


@router.post("/logout")
@idempotent(ttl_seconds=3600)
def logout_user(
    payload: LogoutRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    try:
        auth_service.logout(db, current_user.id, payload.refresh_token)
    except RefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
