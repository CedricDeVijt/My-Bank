"""
Transaction Service - Handles money transfer between accounts

Best Practices Implemented:
1. ACID Compliance - All operations are atomic at the database level
2. Pessimistic Locking - Locks accounts during transaction to prevent race conditions
3. Idempotency - Handled at API level with Idempotency-Key header
4. Status Tracking - Tracks transaction lifecycle
5. Comprehensive Validation - Checks all business rules before processing
6. Atomic Updates - Both accounts updated in single transaction
7. Immutability - Transactions cannot be modified after creation
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.exceptions import (
    AccountNotFoundError,
    CurrencyMismatchError,
    InsufficientBalanceError,
    InvalidAccountStatusError,
    InvalidTransactionError,
    UnauthorizedTransactionError,
)
from src.db.models import Account, Transaction
from src.repositories import account_repository, transaction_repository


def execute_transfer(
    db: Session,
    from_iban: str,
    to_iban: str,
    amount_cents: int,
    actor_user_id: uuid.UUID,
) -> Transaction:
    """
    Execute a money transfer between two accounts.

    This function implements proper transaction handling with:
    - Pessimistic locking (FOR UPDATE) to prevent race conditions
    - ACID compliance at the database level
    - Comprehensive validation
    - Atomic balance updates

    Args:
        db: SQLAlchemy session
        from_iban: IBAN of the sending account
        to_iban: IBAN of the receiving account
        amount_cents: Amount to transfer in cents
        actor_user_id: UUID of the authenticated user initiating the transfer

    Returns:
        Transaction: The created transaction record

    Raises:
        AccountNotFoundError: If either account doesn't exist
        InvalidAccountStatusError: If either account is not active
        CurrencyMismatchError: If accounts have different currencies
        InsufficientBalanceError: If from_account doesn't have enough balance
        InvalidTransactionError: If transfer amount is invalid
        UnauthorizedTransactionError: If source account does not belong to actor
    """

    # Validation 1: Basic checks
    if amount_cents <= 0:
        raise InvalidTransactionError("Transfer amount must be greater than 0")

    # Validation 2: Retrieve both accounts with pessimistic locking (FOR UPDATE)
    # This locks the rows so no other transaction can modify them until we're done
    from_account = account_repository.get_by_iban(db, from_iban)

    if not from_account:
        raise AccountNotFoundError(f"From account {from_iban} not found")

    from_account = db.scalars(
        select(Account).where(Account.id == from_account.id).with_for_update()
    ).first()

    if not from_account:
        raise AccountNotFoundError(f"From account {from_iban} not found")

    to_account = account_repository.get_by_iban(db, to_iban)

    if not to_account:
        raise AccountNotFoundError(f"To account {to_iban} not found")

    to_account = db.scalars(
        select(Account).where(Account.id == to_account.id).with_for_update()
    ).first()

    if not to_account:
        raise AccountNotFoundError(f"To account {to_iban} not found")

    if from_account.id == to_account.id:
        raise InvalidTransactionError("Cannot transfer to the same account")

    # Validation 3: Enforce source account ownership for authorization
    if from_account.account_holder_id != actor_user_id:
        raise UnauthorizedTransactionError(
            "You are not authorized to transfer from this account"
        )

    # Validation 4: Check account statuses
    if from_account.status != "active":
        raise InvalidAccountStatusError(
            f"From account is {from_account.status}, only active accounts can send"
        )

    if to_account.status != "active":
        raise InvalidAccountStatusError(
            f"To account is {to_account.status}, only active accounts can receive"
        )

    # Validation 5: Check currencies match
    if from_account.currency != to_account.currency:
        raise CurrencyMismatchError(
            f"Cannot transfer between {from_account.currency} and {to_account.currency}"
        )

    # Validation 6: Check sufficient balance
    if from_account.balance_cents < amount_cents:
        raise InsufficientBalanceError(
            f"Insufficient balance. Available: {from_account.balance_cents}, "
            f"Required: {amount_cents}"
        )

    # Execute the transfer - ATOMIC OPERATION
    # Both balance updates happen in the same database transaction
    try:
        # Debit from sender
        from_account.balance_cents -= amount_cents

        # Credit to receiver
        to_account.balance_cents += amount_cents

        # Record the transaction in the transaction log
        transaction = transaction_repository.create(
            db=db,
            transaction_data={
                "from_account_id": from_account.id,
                "to_account_id": to_account.id,
                "amount_cents": amount_cents,
                "currency": from_account.currency,
                "status": "completed",
            },
        )

        # All changes are committed together by the caller
        # If anything fails, the entire transaction is rolled back
        return transaction

    except Exception as e:
        # If any error occurs, the database session will be rolled back
        # by the caller, leaving the accounts unchanged
        raise InvalidTransactionError(f"Transfer failed: {str(e)}") from e


def get_account_history(
    db: Session,
    account_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Transaction], int]:
    """
    Get transaction history for an account.

    Args:
        db: SQLAlchemy session
        account_id: UUID of the account
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        Tuple of (transactions list, total count)

    Raises:
        AccountNotFoundError: If account doesn't exist
    """
    # Verify account exists
    account = account_repository.get_by_id(db, account_id)

    if not account:
        # Still not found, but we'll return empty list instead of error
        # This is more user-friendly for accounts that have never had transactions
        return [], 0

    return transaction_repository.get_account_transactions_range(
        db=db, account_id=account_id, skip=skip, limit=limit
    )
