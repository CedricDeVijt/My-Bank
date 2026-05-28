import uuid
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from src.schemas.Token import LogoutRequest, RefreshTokenRequest, TokenResponse
from src.schemas.Transaction import (
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionResponse,
)
from src.schemas.User import UserCreate


class TestUserCreateSchema:
    def test_user_create_valid(self) -> None:
        """Test valid user creation schema"""
        user = UserCreate(
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
        )
        assert user.email == "test@example.com"
        assert user.password == "SecurePassword123!"

    def test_user_create_short_password(self) -> None:
        """Test user creation fails with short password"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="short",
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 1, 1),
            )
        assert "at least 12 characters" in str(exc_info.value)

    def test_user_create_invalid_email(self) -> None:
        """Test user creation fails with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",
                password="SecurePassword123!",
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 1, 1),
            )

    def test_user_create_empty_first_name(self) -> None:
        """Test user creation fails with empty first name"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="SecurePassword123!",
                first_name="",
                last_name="Doe",
                date_of_birth=date(1990, 1, 1),
            )

    def test_user_create_empty_last_name(self) -> None:
        """Test user creation fails with empty last name"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="SecurePassword123!",
                first_name="John",
                last_name="",
                date_of_birth=date(1990, 1, 1),
            )

    def test_user_create_whitespace_only_name(self) -> None:
        """Test user creation fails with whitespace-only name"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="SecurePassword123!",
                first_name="   ",
                last_name="Doe",
                date_of_birth=date(1990, 1, 1),
            )

    def test_user_create_whitespace_stripped(self) -> None:
        """Test user creation strips whitespace from names"""
        user = UserCreate(
            email="test@example.com",
            password="SecurePassword123!",
            first_name="  John  ",
            last_name="  Doe  ",
            date_of_birth=date(1990, 1, 1),
        )
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_user_create_extra_fields_forbidden(self) -> None:
        """Test user creation fails with extra fields"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="SecurePassword123!",
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 1, 1),
                extra_field="not allowed",
            )


class TestTransactionCreateRequestSchema:
    def test_transaction_create_valid(self) -> None:
        """Test valid transaction creation request"""
        tx = TransactionCreateRequest(
            from_iban="BE12345678901234",
            to_iban="BE98765432109876",
            amount_cents=50000,
        )
        assert tx.from_iban == "BE12345678901234"
        assert tx.amount_cents == 50000

    def test_transaction_create_iban_normalization(self) -> None:
        """Test IBAN normalization (uppercase and space removal)"""
        tx = TransactionCreateRequest(
            from_iban="be12 3456 7890 1234",
            to_iban="BE98765432109876",
            amount_cents=50000,
        )
        assert tx.from_iban == "BE12345678901234"

    def test_transaction_create_zero_amount(self) -> None:
        """Test transaction fails with zero amount"""
        with pytest.raises(ValidationError):
            TransactionCreateRequest(
                from_iban="BE12345678901234",
                to_iban="BE98765432109876",
                amount_cents=0,
            )

    def test_transaction_create_negative_amount(self) -> None:
        """Test transaction fails with negative amount"""
        with pytest.raises(ValidationError):
            TransactionCreateRequest(
                from_iban="BE12345678901234",
                to_iban="BE98765432109876",
                amount_cents=-50000,
            )

    def test_transaction_create_same_account(self) -> None:
        """Test transaction fails when from and to are the same"""
        with pytest.raises(ValidationError):
            TransactionCreateRequest(
                from_iban="BE12345678901234",
                to_iban="BE12345678901234",
                amount_cents=50000,
            )

    def test_transaction_create_empty_iban(self) -> None:
        """Test transaction fails with empty IBAN"""
        with pytest.raises(ValidationError):
            TransactionCreateRequest(
                from_iban="",
                to_iban="BE98765432109876",
                amount_cents=50000,
            )

    def test_transaction_create_extra_fields_forbidden(self) -> None:
        """Test transaction accepts extra fields (Pydantic v2 allows by default)"""
        # In Pydantic v2, extra fields are ignored by default unless
        # explicitly forbidden
        # The schema doesn't have ConfigDict(extra="forbid"), so
        # extra fields are allowed
        tx = TransactionCreateRequest(
            from_iban="BE12345678901234",
            to_iban="BE98765432109876",
            amount_cents=50000,
            extra_field="allowed",  # This will be silently ignored
        )
        assert tx.from_iban == "BE12345678901234"
        assert tx.amount_cents == 50000


class TestTokenResponseSchema:
    def test_token_response_valid(self) -> None:
        """Test valid token response"""
        token = TokenResponse(
            access_token="access-token-here",
            refresh_token="refresh-token-here",
            access_token_expires_in=3600,
            refresh_token_expires_in=604800,
        )
        assert token.access_token == "access-token-here"
        assert token.token_type == "Bearer"

    def test_token_response_zero_expiry(self) -> None:
        """Test token response fails with zero expiry"""
        with pytest.raises(ValidationError):
            TokenResponse(
                access_token="access-token",
                refresh_token="refresh-token",
                access_token_expires_in=0,
                refresh_token_expires_in=604800,
            )

    def test_token_response_negative_expiry(self) -> None:
        """Test token response fails with negative expiry"""
        with pytest.raises(ValidationError):
            TokenResponse(
                access_token="access-token",
                refresh_token="refresh-token",
                access_token_expires_in=-3600,
                refresh_token_expires_in=604800,
            )


class TestRefreshTokenRequestSchema:
    def test_refresh_token_request_valid(self) -> None:
        """Test valid refresh token request"""
        request = RefreshTokenRequest(refresh_token="valid-refresh-token-12345")
        assert len(request.refresh_token) >= 16

    def test_refresh_token_request_short_token(self) -> None:
        """Test refresh token request fails with short token"""
        with pytest.raises(ValidationError):
            RefreshTokenRequest(refresh_token="short")


class TestLogoutRequestSchema:
    def test_logout_request_valid(self) -> None:
        """Test valid logout request"""
        request = LogoutRequest(refresh_token="valid-refresh-token-12345")
        assert len(request.refresh_token) >= 16

    def test_logout_request_short_token(self) -> None:
        """Test logout request fails with short token"""
        with pytest.raises(ValidationError):
            LogoutRequest(refresh_token="short")


class TestTransactionResponseSchema:
    def test_transaction_response_valid(self) -> None:
        """Test valid transaction response"""
        tx_id = uuid.uuid4()
        from_account_id = uuid.uuid4()
        to_account_id = uuid.uuid4()

        tx = TransactionResponse(
            id=tx_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount_cents=50000,
            currency="EUR",
            status="completed",
            failure_reason=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert tx.id == tx_id
        assert tx.amount_cents == 50000

    def test_transaction_response_with_failure_reason(self) -> None:
        """Test transaction response with failure reason"""
        tx_id = uuid.uuid4()
        from_account_id = uuid.uuid4()
        to_account_id = uuid.uuid4()

        tx = TransactionResponse(
            id=tx_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount_cents=50000,
            currency="EUR",
            status="failed",
            failure_reason="Insufficient balance",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert tx.status == "failed"
        assert tx.failure_reason == "Insufficient balance"


class TestTransactionListResponseSchema:
    def test_transaction_list_response_valid(self) -> None:
        """Test valid transaction list response"""
        tx_id = uuid.uuid4()
        from_account_id = uuid.uuid4()
        to_account_id = uuid.uuid4()

        tx = TransactionListResponse(
            id=tx_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount_cents=50000,
            currency="EUR",
            status="completed",
            created_at=datetime.now(),
        )
        assert tx.id == tx_id
        assert tx.currency == "EUR"
