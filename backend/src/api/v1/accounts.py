from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.core.idempotency import idempotent
from src.db import get_db
from src.db.models import User
from src.schemas.Account import AccountCreate, AccountListResponse, AccountResponse
from src.services import account_service

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=AccountListResponse)
def list_accounts(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AccountListResponse:
    accounts = account_service.list_user_accounts(db, current_user.id)

    return AccountListResponse(
        accounts=[
            AccountResponse(
                account_id=acc.id,
                account_number=account_service.mask_account_number(acc.account_number),
                iban=account_service.mask_iban(acc.iban),
                type=acc.type,
                currency=acc.currency,
                balance_cents=acc.balance_cents,
                status=acc.status,
                created_at=acc.created_at,
            )
            for acc in accounts
        ]
    )


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
@idempotent(ttl_seconds=3600)
def create_account(
    payload: AccountCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AccountResponse:
    account = account_service.create(
        db=db,
        user_id=current_user.id,
        account_type=payload.type,
        currency=payload.currency,
    )

    return AccountResponse(
        account_id=account.id,
        account_number=account.account_number,
        iban=account.iban,
        type=account.type,
        currency=account.currency,
        balance_cents=account.balance_cents,
        status=account.status,
        created_at=account.created_at,
    )
