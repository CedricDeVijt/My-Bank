import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Account


def get_by_id(db: Session, account_id: uuid.UUID) -> Account | None:
    """Retrieve an account by ID"""
    stmt = select(Account).where(Account.id == account_id)
    return db.scalars(stmt).first()


def get_by_user_id(db: Session, user_id: uuid.UUID) -> list[Account]:
    """Get all accounts for a user"""
    stmt = select(Account).where(Account.account_holder_id == user_id)
    return list(db.scalars(stmt).all())


def get_by_account_number(db: Session, account_number: str) -> Account | None:
    """Retrieve an account by account number"""
    stmt = select(Account).where(Account.account_number == account_number)
    return db.scalars(stmt).first()


def get_by_iban(db: Session, iban: str) -> Account | None:
    """Retrieve an account by IBAN"""
    normalized_iban = iban.replace(" ", "").upper()
    stmt = select(Account).where(Account.iban == normalized_iban)
    return db.scalars(stmt).first()


def create(db: Session, account_data: dict[str, Any]) -> Account:
    """Create a new account"""
    account = Account(**account_data)
    db.add(account)
    return account
