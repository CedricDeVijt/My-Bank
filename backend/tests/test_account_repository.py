import uuid
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from src.repositories import account_repository


def test_get_by_id_and_account_number(
    db_session: Session,
    user_factory: Any,
    account_factory: Any,
) -> None:
    user = user_factory()
    account = account_factory(
        account_holder_id=user.id,
        account_number="111122223333",
        iban="BE12111122223333",
    )

    by_id = account_repository.get_by_id(db_session, account.id)
    by_number = account_repository.get_by_account_number(db_session, "111122223333")

    assert by_id is not None
    assert by_number is not None
    assert by_id.id == account.id
    assert by_number.id == account.id


def test_get_by_user_id_returns_only_user_accounts(
    db_session: Session,
    user_factory: Any,
    account_factory: Any,
) -> None:
    owner = user_factory(email="owner@example.com")
    other = user_factory(email="other@example.com")

    account_factory(account_holder_id=owner.id)
    account_factory(account_holder_id=owner.id)
    account_factory(account_holder_id=other.id)

    accounts = account_repository.get_by_user_id(db_session, owner.id)

    assert len(accounts) == 2
    assert all(account.account_holder_id == owner.id for account in accounts)


def test_get_by_iban_normalizes_input(
    db_session: Session,
    user_factory: Any,
    account_factory: Any,
) -> None:
    user = user_factory()
    account = account_factory(account_holder_id=user.id, iban="BE12123456789012")

    result = account_repository.get_by_iban(db_session, "be12 1234 5678 9012")

    assert result is not None
    assert result.id == account.id


def test_create_adds_account_to_session(db_session: Session, user_factory: Any) -> None:
    user = user_factory()

    account = account_repository.create(
        db_session,
        {
            "account_number": "999900001111",
            "iban": "BE12999900001111",
            "type": "checking",
            "currency": "EUR",
            "balance_cents": 0,
            "status": "active",
            "created_at": date.today(),
            "account_holder_id": user.id,
        },
    )
    db_session.commit()

    fetched = account_repository.get_by_id(db_session, account.id)
    assert fetched is not None


def test_get_by_id_returns_none_for_unknown_id(db_session: Session) -> None:
    assert account_repository.get_by_id(db_session, uuid.uuid4()) is None
