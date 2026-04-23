from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    RefreshTokenError,
)
from src.db import get_db
from src.schemas.Token import RefreshTokenRequest, TokenResponse
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
        user_id=str(created.id), email=created.email, status="pending_verification"
    )


@router.post("/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db())):
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
