from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.exceptions import EmailAlreadyRegisteredError
from src.db import get_db
from src.schemas.User import UserCreate, UserResponse
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
