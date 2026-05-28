import uuid

from sqlalchemy.orm import Session

from src.repositories import transaction_repository


class TestTransactionRepositoryCreate:
    def test_create_transaction_success(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test creating a transaction"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        transaction_data = {
            "from_account_id": from_account.id,
            "to_account_id": to_account.id,
            "amount_cents": 50000,
            "currency": "EUR",
            "status": "completed",
        }

        transaction = transaction_repository.create(db_session, transaction_data)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.from_account_id == from_account.id
        assert transaction.to_account_id == to_account.id
        assert transaction.amount_cents == 50000
        assert transaction.currency == "EUR"
        assert transaction.status == "completed"


class TestTransactionRepositoryGetById:
    def test_get_by_id_found(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test retrieving a transaction by ID"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        transaction_data = {
            "from_account_id": from_account.id,
            "to_account_id": to_account.id,
            "amount_cents": 50000,
            "currency": "EUR",
            "status": "completed",
        }
        transaction = transaction_repository.create(db_session, transaction_data)
        db_session.commit()

        result = transaction_repository.get_by_id(db_session, transaction.id)

        assert result is not None
        assert result.id == transaction.id
        assert result.amount_cents == 50000

    def test_get_by_id_not_found(self, db_session: Session) -> None:
        """Test retrieving a transaction that doesn't exist"""
        random_id = uuid.uuid4()

        result = transaction_repository.get_by_id(db_session, random_id)

        assert result is None


class TestTransactionRepositoryGetByAccount:
    def test_get_by_account_as_sender(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test retrieving transactions where account is sender"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        transaction = transaction_repository.create(
            db_session,
            {
                "from_account_id": from_account.id,
                "to_account_id": to_account.id,
                "amount_cents": 50000,
                "currency": "EUR",
                "status": "completed",
            },
        )
        db_session.commit()

        result = transaction_repository.get_by_account(db_session, from_account.id)

        assert len(result) == 1
        assert result[0].id == transaction.id

    def test_get_by_account_as_recipient(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test retrieving transactions where account is recipient"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        transaction = transaction_repository.create(
            db_session,
            {
                "from_account_id": from_account.id,
                "to_account_id": to_account.id,
                "amount_cents": 50000,
                "currency": "EUR",
                "status": "completed",
            },
        )
        db_session.commit()

        result = transaction_repository.get_by_account(db_session, to_account.id)

        assert len(result) == 1
        assert result[0].id == transaction.id

    def test_get_by_account_both_roles(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test retrieving transactions where account is both sender and recipient"""
        user = user_factory()
        account1 = account_factory(account_holder_id=user.id)
        account2 = account_factory(account_holder_id=user.id)
        account3 = account_factory(account_holder_id=user.id)

        # account1 sends to account2
        tx1 = transaction_repository.create(
            db_session,
            {
                "from_account_id": account1.id,
                "to_account_id": account2.id,
                "amount_cents": 10000,
                "currency": "EUR",
                "status": "completed",
            },
        )
        # account2 sends to account1
        tx2 = transaction_repository.create(
            db_session,
            {
                "from_account_id": account2.id,
                "to_account_id": account1.id,
                "amount_cents": 20000,
                "currency": "EUR",
                "status": "completed",
            },
        )
        # account3 sends to account1 (not relevant)
        tx3 = transaction_repository.create(
            db_session,
            {
                "from_account_id": account3.id,
                "to_account_id": account1.id,
                "amount_cents": 30000,
                "currency": "EUR",
                "status": "completed",
            },
        )
        db_session.commit()

        result = transaction_repository.get_by_account(db_session, account1.id)

        assert len(result) == 3
        transaction_ids = {tx.id for tx in result}
        assert tx1.id in transaction_ids
        assert tx2.id in transaction_ids
        assert tx3.id in transaction_ids

    def test_get_by_account_empty(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test retrieving transactions for an account with no transactions"""
        user = user_factory()
        account = account_factory(account_holder_id=user.id)

        result = transaction_repository.get_by_account(db_session, account.id)

        assert len(result) == 0

    def test_get_by_account_pagination(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test pagination of transactions"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        # Create 5 transactions
        for i in range(5):
            transaction_repository.create(
                db_session,
                {
                    "from_account_id": from_account.id,
                    "to_account_id": to_account.id,
                    "amount_cents": 10000 * (i + 1),
                    "currency": "EUR",
                    "status": "completed",
                },
            )
        db_session.commit()

        # Get first 2
        result = transaction_repository.get_by_account(
            db_session, from_account.id, skip=0, limit=2
        )
        assert len(result) == 2

        # Get next 2
        result = transaction_repository.get_by_account(
            db_session, from_account.id, skip=2, limit=2
        )
        assert len(result) == 2

        # Get last 1
        result = transaction_repository.get_by_account(
            db_session, from_account.id, skip=4, limit=2
        )
        assert len(result) == 1

    def test_get_by_account_ordering(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test that transactions are ordered by created_at descending"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        # Create transactions
        transactions = []
        for i in range(3):
            tx = transaction_repository.create(
                db_session,
                {
                    "from_account_id": from_account.id,
                    "to_account_id": to_account.id,
                    "amount_cents": 10000 * (i + 1),
                    "currency": "EUR",
                    "status": "completed",
                },
            )
            transactions.append(tx)
        db_session.commit()

        result = transaction_repository.get_by_account(db_session, from_account.id)

        # Most recent should be first (reverse order of creation)
        assert result[0].amount_cents == 30000
        assert result[1].amount_cents == 20000
        assert result[2].amount_cents == 10000


class TestTransactionRepositoryGetAccountTransactionsRange:
    def test_get_account_transactions_range_with_count(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test retrieving transactions with total count"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        # Create 5 transactions
        for i in range(5):
            transaction_repository.create(
                db_session,
                {
                    "from_account_id": from_account.id,
                    "to_account_id": to_account.id,
                    "amount_cents": 10000 * (i + 1),
                    "currency": "EUR",
                    "status": "completed",
                },
            )
        db_session.commit()

        transactions, total = transaction_repository.get_account_transactions_range(
            db_session, from_account.id, skip=0, limit=2
        )

        assert len(transactions) == 2
        assert total == 5

    def test_get_account_transactions_range_pagination(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test pagination with get_account_transactions_range"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id)
        to_account = account_factory(account_holder_id=user.id)

        # Create 10 transactions
        for i in range(10):
            transaction_repository.create(
                db_session,
                {
                    "from_account_id": from_account.id,
                    "to_account_id": to_account.id,
                    "amount_cents": 10000 * (i + 1),
                    "currency": "EUR",
                    "status": "completed",
                },
            )
        db_session.commit()

        # First page
        transactions, total = transaction_repository.get_account_transactions_range(
            db_session, from_account.id, skip=0, limit=3
        )
        assert len(transactions) == 3
        assert total == 10

        # Second page
        transactions, total = transaction_repository.get_account_transactions_range(
            db_session, from_account.id, skip=3, limit=3
        )
        assert len(transactions) == 3
        assert total == 10

    def test_get_account_transactions_range_empty(
        self, db_session: Session, account_factory, user_factory
    ) -> None:
        """Test get_account_transactions_range for account with no transactions"""
        user = user_factory()
        account = account_factory(account_holder_id=user.id)

        transactions, total = transaction_repository.get_account_transactions_range(
            db_session, account.id, skip=0, limit=50
        )

        assert len(transactions) == 0
        assert total == 0
