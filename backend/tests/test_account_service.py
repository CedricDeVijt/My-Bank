from typing import Any

from sqlalchemy.orm import Session

from src.services import account_service


def test_mask_account_number() -> None:
    assert account_service.mask_account_number("123456789012") == "****9012"


def test_mask_iban() -> None:
    assert account_service.mask_iban("BE12123456789012") == "BE12****9012"


def test_create_retries_when_generated_values_collide(
    db_session: Session,
    user_factory: Any,
    account_factory: Any,
    monkeypatch: Any,
) -> None:
    user = user_factory()

    account_factory(
        account_holder_id=user.id,
        account_number="111111111111",
        iban="BE12111111111111",
    )

    generated_numbers = iter(["111111111111", "222222222222"])
    generated_ibans = iter(["BE12111111111111", "BE12222222222222"])

    monkeypatch.setattr(
        account_service,
        "_generate_account_number",
        lambda: next(generated_numbers),
    )
    monkeypatch.setattr(
        account_service,
        "_generate_iban",
        lambda: next(generated_ibans),
    )

    new_account = account_service.create(
        db=db_session,
        user_id=user.id,
        account_type="checking",
        currency="EUR",
    )

    assert new_account.account_number == "222222222222"
    assert new_account.iban == "BE12222222222222"


def test_list_user_accounts_delegates_to_repository(
    db_session: Session,
    user_factory: Any,
    account_factory: Any,
) -> None:
    owner = user_factory(email="owner-service@example.com")
    other = user_factory(email="other-service@example.com")

    owner_account = account_factory(account_holder_id=owner.id)
    account_factory(account_holder_id=other.id)

    result = account_service.list_user_accounts(db_session, owner.id)

    assert len(result) == 1
    assert result[0].id == owner_account.id
