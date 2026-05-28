from datetime import date

import pytest
from pydantic import ValidationError

from src.schemas.Account import AccountCreate, AccountResponse


def test_account_create_accepts_valid_payload() -> None:
    payload = AccountCreate(type="checking", currency="eur")

    assert payload.type == "checking"
    assert payload.currency == "eur"


def test_account_create_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        AccountCreate(type="business", currency="EUR")


def test_account_create_rejects_invalid_currency_length() -> None:
    with pytest.raises(ValidationError):
        AccountCreate(type="savings", currency="EURO")


def test_account_response_from_attributes() -> None:
    class AccountLike:
        account_id = "00000000-0000-0000-0000-000000000001"
        account_number = "123456789012"
        iban = "BE12123456789012"
        type = "checking"
        currency = "EUR"
        balance_cents = 500
        status = "active"
        created_at = date(2026, 1, 1)

    model = AccountResponse.model_validate(AccountLike())

    assert str(model.account_id) == "00000000-0000-0000-0000-000000000001"
    assert model.created_at == date(2026, 1, 1)
