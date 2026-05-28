import uuid

import pytest
from sqlalchemy.orm import Session

from src.core.exceptions import (
    AccountNotFoundError,
    CurrencyMismatchError,
    InsufficientBalanceError,
    InvalidAccountStatusError,
    InvalidTransactionError,
    UnauthorizedTransactionError,
)
from src.services import transaction_service


class TestTransactionServiceExecuteTransferValidation:
    def test_execute_transfer_zero_amount(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails with zero amount"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id)

        with pytest.raises(InvalidTransactionError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=0,
                actor_user_id=user.id,
            )

    def test_execute_transfer_negative_amount(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails with negative amount"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id)

        with pytest.raises(InvalidTransactionError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=-50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_same_account(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when from and to accounts are the same"""
        user = user_factory()
        account = account_factory(account_holder_id=user.id, balance_cents=100000)

        with pytest.raises(InvalidTransactionError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=account.iban,
                to_iban=account.iban,
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_from_account_not_found(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when from account doesn't exist"""
        user = user_factory()
        to_account = account_factory(account_holder_id=user.id)

        with pytest.raises(AccountNotFoundError):
            transaction_service.execute_transfer(
                db_session,
                from_iban="NONEXISTENT",
                to_iban=to_account.iban,
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_to_account_not_found(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when to account doesn't exist"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)

        with pytest.raises(AccountNotFoundError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban="NONEXISTENT",
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_insufficient_balance(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails with insufficient balance"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=30000)
        to_account = account_factory(account_holder_id=user.id)

        with pytest.raises(InsufficientBalanceError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_currency_mismatch(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when currencies don't match"""
        user = user_factory()
        from_account = account_factory(
            account_holder_id=user.id, balance_cents=100000, currency="EUR"
        )
        to_account = account_factory(account_holder_id=user.id, currency="USD")

        with pytest.raises(CurrencyMismatchError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_from_account_inactive(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when from account is not active"""
        user = user_factory()
        from_account = account_factory(
            account_holder_id=user.id, balance_cents=100000, status="frozen"
        )
        to_account = account_factory(account_holder_id=user.id)

        with pytest.raises(InvalidAccountStatusError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_to_account_inactive(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when to account is not active"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id, status="closed")

        with pytest.raises(InvalidAccountStatusError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=50000,
                actor_user_id=user.id,
            )

    def test_execute_transfer_unauthorized(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer fails when user doesn't own from account"""
        user1 = user_factory()
        user2 = user_factory()
        from_account = account_factory(account_holder_id=user1.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user2.id)

        with pytest.raises(UnauthorizedTransactionError):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=50000,
                actor_user_id=user2.id,  # user2 trying to transfer from user1's account
            )


class TestTransactionServiceExecuteTransferSuccess:
    def test_execute_transfer_success(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test successful transfer"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id, balance_cents=50000)

        transaction = transaction_service.execute_transfer(
            db_session,
            from_iban=from_account.iban,
            to_iban=to_account.iban,
            amount_cents=30000,
            actor_user_id=user.id,
        )
        db_session.commit()
        db_session.refresh(from_account)
        db_session.refresh(to_account)

        assert transaction is not None
        assert transaction.amount_cents == 30000
        assert transaction.currency == "EUR"
        assert transaction.status == "completed"
        assert from_account.balance_cents == 70000
        assert to_account.balance_cents == 80000

    def test_execute_transfer_different_users(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer between accounts of different users"""
        user1 = user_factory()
        user2 = user_factory()
        account1 = account_factory(account_holder_id=user1.id, balance_cents=100000)
        account2 = account_factory(account_holder_id=user2.id, balance_cents=50000)

        transaction = transaction_service.execute_transfer(
            db_session,
            from_iban=account1.iban,
            to_iban=account2.iban,
            amount_cents=25000,
            actor_user_id=user1.id,
        )
        db_session.commit()
        db_session.refresh(account1)
        db_session.refresh(account2)

        assert transaction.amount_cents == 25000
        assert account1.balance_cents == 75000
        assert account2.balance_cents == 75000

    def test_execute_transfer_exact_balance(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer with exactly the available balance"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=50000)
        to_account = account_factory(account_holder_id=user.id, balance_cents=0)

        transaction_service.execute_transfer(
            db_session,
            from_iban=from_account.iban,
            to_iban=to_account.iban,
            amount_cents=50000,
            actor_user_id=user.id,
        )
        db_session.commit()
        db_session.refresh(from_account)
        db_session.refresh(to_account)

        assert from_account.balance_cents == 0
        assert to_account.balance_cents == 50000

    def test_execute_transfer_one_cent(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test transfer with minimum amount (1 cent)"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100)
        to_account = account_factory(account_holder_id=user.id, balance_cents=0)

        transaction_service.execute_transfer(
            db_session,
            from_iban=from_account.iban,
            to_iban=to_account.iban,
            amount_cents=1,
            actor_user_id=user.id,
        )
        db_session.commit()
        db_session.refresh(from_account)
        db_session.refresh(to_account)

        assert from_account.balance_cents == 99
        assert to_account.balance_cents == 1


class TestTransactionServiceGetAccountHistory:
    def test_get_account_history_empty(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test getting history for account with no transactions"""
        user = user_factory()
        account = account_factory(account_holder_id=user.id)

        transactions, total = transaction_service.get_account_history(
            db_session, account.id
        )

        assert len(transactions) == 0
        assert total == 0

    def test_get_account_history_success(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test getting account transaction history"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=500000)
        to_account = account_factory(account_holder_id=user.id)

        # Create multiple transactions
        for i in range(3):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=10000 * (i + 1),
                actor_user_id=user.id,
            )
            db_session.commit()

        transactions, total = transaction_service.get_account_history(
            db_session, from_account.id
        )

        assert len(transactions) == 3
        assert total == 3

    def test_get_account_history_pagination(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test pagination of account history"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=1000000)
        to_account = account_factory(account_holder_id=user.id)

        # Create 10 transactions
        for _ in range(10):
            transaction_service.execute_transfer(
                db_session,
                from_iban=from_account.iban,
                to_iban=to_account.iban,
                amount_cents=10000,
                actor_user_id=user.id,
            )
            db_session.commit()

        # First page
        transactions, total = transaction_service.get_account_history(
            db_session, from_account.id, skip=0, limit=3
        )
        assert len(transactions) == 3

        assert total == 10

        # Second page
        transactions, total = transaction_service.get_account_history(
            db_session, from_account.id, skip=3, limit=3
        )
        assert len(transactions) == 3
        assert total == 10

    def test_get_account_history_nonexistent_account(self, db_session: Session) -> None:
        """Test getting history for nonexistent account"""
        nonexistent_id = uuid.uuid4()

        transactions, total = transaction_service.get_account_history(
            db_session, nonexistent_id
        )

        assert len(transactions) == 0
        assert total == 0

    def test_get_account_history_both_roles(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test getting history for account that's both sender and recipient"""
        user = user_factory()
        account1 = account_factory(account_holder_id=user.id, balance_cents=500000)
        account2 = account_factory(account_holder_id=user.id, balance_cents=500000)

        # account1 -> account2
        transaction_service.execute_transfer(
            db_session,
            from_iban=account1.iban,
            to_iban=account2.iban,
            amount_cents=10000,
            actor_user_id=user.id,
        )
        db_session.commit()

        # account2 -> account1
        transaction_service.execute_transfer(
            db_session,
            from_iban=account2.iban,
            to_iban=account1.iban,
            amount_cents=20000,
            actor_user_id=user.id,
        )
        db_session.commit()

        transactions, total = transaction_service.get_account_history(
            db_session, account1.id
        )

        assert len(transactions) == 2
        assert total == 2
