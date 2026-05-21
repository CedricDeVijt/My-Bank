import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.db.models import Transaction


def create(db: Session, transaction_data: dict) -> Transaction:
    """Create a new transaction record"""
    transaction = Transaction(**transaction_data)
    db.add(transaction)
    return transaction


def get_by_id(db: Session, transaction_id: uuid.UUID) -> Transaction | None:
    """Retrieve a transaction by ID"""
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    return db.scalars(stmt).first()


def get_by_account(
    db: Session,
    account_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> list[Transaction]:
    """Get all transactions for an account (as sender or recipient)"""
    stmt = (
        select(Transaction)
        .where(
            (Transaction.from_account_id == account_id)
            | (Transaction.to_account_id == account_id)
        )
        .order_by(Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_account_transactions_range(
    db: Session,
    account_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Transaction], int]:
    """Get transactions for an account with total count for pagination"""
    # Get count
    count_stmt = select(Transaction).where(
        (Transaction.from_account_id == account_id)
        | (Transaction.to_account_id == account_id)
    )
    total = len(db.scalars(count_stmt).all())

    # Get paginated results
    transactions = get_by_account(db, account_id, skip, limit)
    return transactions, total
