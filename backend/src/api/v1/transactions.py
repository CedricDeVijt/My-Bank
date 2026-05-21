from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.api.dependencies import get_current_user
from src.core.exceptions import (
    AccountNotFoundError,
    CurrencyMismatchError,
    InsufficientBalanceError,
    InvalidAccountStatusError,
    InvalidTransactionError,
    TransactionError,
    UnauthorizedTransactionError,
)
from src.core.idempotency import idempotent
from src.db import get_db
from src.schemas.Transaction import (
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionResponse,
)
from src.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def handle_transaction_error(error: Exception) -> HTTPException:
    """Convert business logic exceptions to HTTP exceptions"""
    if isinstance(error, AccountNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    elif isinstance(error, InsufficientBalanceError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    elif isinstance(error, InvalidAccountStatusError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    elif isinstance(error, InvalidTransactionError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    elif isinstance(error, CurrencyMismatchError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    elif isinstance(error, UnauthorizedTransactionError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    elif isinstance(error, TransactionError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=TransactionResponse
)
@idempotent(ttl_seconds=3600)
def create_transaction(
    payload: TransactionCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TransactionResponse:
    """
    Execute a money transfer between accounts.

    This endpoint:
    - Validates the request (amounts, accounts, authorization)
    - Uses idempotency key for safe retry (Idempotency-Key header)
    - Executes atomic transfer with pessimistic locking
    - Returns transaction details

    Headers:
    - Idempotency-Key: Unique key to prevent duplicate processing (recommended)

    Returns:
        TransactionResponse: Details of the created transaction

    Raises:
        404: If account not found
        403: If source account does not belong to authenticated user
        400: If insufficient balance or invalid account status or currency mismatch
        422: If validation fails (same account, zero/negative amount, etc.)
    """
    try:
        transaction = transaction_service.execute_transfer(
            db=db,
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount_cents=payload.amount_cents,
            actor_user_id=current_user.id,
        )

        # Commit the database transaction atomically
        db.commit()
        db.refresh(transaction)

        return TransactionResponse.model_validate(transaction)

    except TransactionError as e:
        db.rollback()
        raise handle_transaction_error(e)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[TransactionListResponse]
)
def list_transactions(
    account_id: str = Query(None, description="Filter transactions by account ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[TransactionListResponse]:
    """
    Get transaction history for an account.

    Query Parameters:
    - account_id: The account to get transactions for (required)
    - skip: Pagination offset (default: 0)
    - limit: Max results per page (default: 50, max: 100)

    Returns:
        List of transactions for the specified account

    Raises:
        400: If account_id is not provided
        404: If account not found (though we allow zero transactions)
    """
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="account_id query parameter is required",
        )

    try:
        import uuid

        # Parse account_id as UUID
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid account_id format",
            )

        transactions, total = transaction_service.get_account_history(
            db=db,
            account_id=account_uuid,
            skip=skip,
            limit=limit,
        )

        return [TransactionListResponse.model_validate(tx) for tx in transactions]

    except AccountNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions",
        )
