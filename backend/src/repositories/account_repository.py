import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.db.models import Account


def get_by_user_id(db: Session, user_id: uuid.UUID) -> list[Account]:
    stmt = select(Account).where(Account.account_holder_id == user_id)
    return list(db.scalars(stmt).all())


def get_by_account_number(db: Session, account_number: str) -> Account | None:
    stmt = select(Account).where(Account.account_number == account_number)
    return db.scalars(stmt).first()


def get_by_iban(db: Session, iban: str) -> Account | None:
    stmt = select(Account).where(Account.iban == iban)
    return db.scalars(stmt).first()


def create(db: Session, account_data: dict) -> Account:
    account = Account(**account_data)
    db.add(account)
    return account
