from fastapi import APIRouter, Depends

from src.schemas.User import UserResponse
from src.api.dependencies import get_current_user
from src.db.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(
        current_user: User = Depends(get_current_user),
):
    return UserResponse(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
    )
