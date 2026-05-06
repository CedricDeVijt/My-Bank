from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from src.api.dependencies import get_current_user
from src.core.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    RefreshTokenError,
)
from src.db import get_db
from src.db.models import User
from src.schemas.Token import LogoutRequest, RefreshTokenRequest, TokenResponse
from src.schemas.User import UserCreate, UserLogin, UserResponse
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:

        created = auth_service.register_user(payload=user, db=db)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    return UserResponse(
        first_name=created.first_name, last_name=created.last_name, email=created.email
    )


@router.post("/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
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
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token(
        payload: RefreshTokenRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    try:
        access_token, refresh_token = auth_service.refresh_tokens(
            db, payload.refresh_token
        )
    except RefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout_user(
    paylaod: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        auth_service.logout(db, current_user.id, paylaod.refresh_token)
    except RefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
