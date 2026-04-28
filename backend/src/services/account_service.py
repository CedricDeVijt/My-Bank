import random
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session
from src.db.models import Account
from src.repositories import account_repository


def mask_account_number(value: str) -> str:
    return f"****{value[-4:]}"


def mask_iban(value: str) -> str:
    return f"{value[:4]}****{value[-4:]}"


def _generate_account_number() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def _generate_iban() -> str:
    bban = "".join(str(random.randint(0, 9)) for _ in range(12))

    rearranged = bban + "BE00"
    numeric = ""

    for ch in rearranged:
        if ch.isalpha():
            numeric += str(ord(ch) - 55)
        else:
            numeric += ch

    check_digits = 98 - (int(numeric) % 97)

    return f"BE{check_digits:02d}{bban}"


def create(
    db: Session, user_id: uuid.UUID, account_type: str, currency: str
) -> Account:
    account_number = _generate_account_number()
    while account_repository.get_by_account_number(db, account_number):
        account_number = _generate_account_number()

    iban = _generate_iban()
    while account_repository.get_by_iban(db, iban):
        iban = _generate_iban()

    account = account_repository.create(
        db,
        {
            "account_number": account_number,
            "iban": iban,
            "type": account_type,
            "currency": currency,
            "balance_cents": 0,
            "status": "active",
            "created_at": datetime.now(UTC),
            "account_holder_id": user_id,
        },
    )
    db.commit()
    db.refresh(account)
    return account


def list_user_accounts(db: Session, user_id: uuid.UUID) -> list[Account]:
    return account_repository.get_by_user_id(db, user_id)
