import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pydantic import ValidationError
from src.api.v1.transactions import list_transactions
from src.core.exceptions import UnauthorizedTransactionError
from src.schemas.Transaction import TransactionCreateRequest
from src.services.transaction_service import execute_transfer


class TransactionIbanTests(TestCase):
    def test_transaction_create_request_normalizes_ibans(self):
        payload = TransactionCreateRequest(
            from_iban=" be12 3456 7890 1234 ",
            to_iban="be12 3456 7890 1235",
            amount_cents=1250,
        )

        self.assertEqual(payload.from_iban, "BE12345678901234")
        self.assertEqual(payload.to_iban, "BE12345678901235")

    def test_transaction_create_request_rejects_same_iban(self):
        with self.assertRaises(ValidationError):
            TransactionCreateRequest(
                from_iban="BE12345678901234",
                to_iban="be12 3456 7890 1234",
                amount_cents=1250,
            )

    @patch("src.services.transaction_service.transaction_repository.create")
    @patch("src.services.transaction_service.account_repository.get_by_iban")
    def test_execute_transfer_uses_ibans_and_updates_balances(
        self,
        mock_get_by_iban,
        mock_create_transaction,
    ):
        owner_id = uuid.uuid4()
        from_account = SimpleNamespace(
            id=uuid.uuid4(),
            account_holder_id=owner_id,
            status="active",
            currency="EUR",
            balance_cents=10_000,
        )
        to_account = SimpleNamespace(
            id=uuid.uuid4(),
            account_holder_id=uuid.uuid4(),
            status="active",
            currency="EUR",
            balance_cents=500,
        )
        transaction = SimpleNamespace(id=uuid.uuid4())
        db = MagicMock()
        db.scalars.side_effect = [
            MagicMock(first=MagicMock(return_value=from_account)),
            MagicMock(first=MagicMock(return_value=to_account)),
        ]
        mock_get_by_iban.side_effect = [from_account, to_account]
        mock_create_transaction.return_value = transaction

        result = execute_transfer(
            db=db,
            from_iban="be12 3456 7890 1234",
            to_iban="BE12345678901235",
            amount_cents=2_500,
            actor_user_id=owner_id,
        )

        self.assertIs(result, transaction)
        self.assertEqual(from_account.balance_cents, 7_500)
        self.assertEqual(to_account.balance_cents, 3_000)
        self.assertEqual(
            mock_get_by_iban.call_args_list[0].args[1], "be12 3456 7890 1234"
        )
        self.assertEqual(mock_get_by_iban.call_args_list[1].args[1], "BE12345678901235")
        mock_create_transaction.assert_called_once()
        self.assertEqual(
            mock_create_transaction.call_args.kwargs["transaction_data"][
                "from_account_id"
            ],
            from_account.id,
        )
        self.assertEqual(
            mock_create_transaction.call_args.kwargs["transaction_data"][
                "to_account_id"
            ],
            to_account.id,
        )

    @patch("src.services.transaction_service.account_repository.get_by_iban")
    def test_execute_transfer_blocks_non_owner(self, mock_get_by_iban):
        owner_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        from_account = SimpleNamespace(
            id=uuid.uuid4(),
            account_holder_id=other_user_id,
            status="active",
            currency="EUR",
            balance_cents=10_000,
        )
        to_account = SimpleNamespace(
            id=uuid.uuid4(),
            account_holder_id=uuid.uuid4(),
            status="active",
            currency="EUR",
            balance_cents=500,
        )
        db = MagicMock()
        db.scalars.side_effect = [
            MagicMock(first=MagicMock(return_value=from_account)),
            MagicMock(first=MagicMock(return_value=to_account)),
        ]
        mock_get_by_iban.side_effect = [from_account, to_account]

        with self.assertRaises(UnauthorizedTransactionError):
            execute_transfer(
                db=db,
                from_iban="BE12345678901234",
                to_iban="BE12345678901235",
                amount_cents=2_500,
                actor_user_id=owner_id,
            )

    @patch("src.api.v1.transactions.account_repository.get_by_iban")
    @patch("src.api.v1.transactions.transaction_service.get_account_history")
    def test_list_transactions_accepts_iban_filter(
        self,
        mock_get_account_history,
        mock_get_by_iban,
    ):
        account = SimpleNamespace(id=uuid.uuid4())
        tx = SimpleNamespace(
            id=uuid.uuid4(),
            from_account_id=uuid.uuid4(),
            to_account_id=uuid.uuid4(),
            amount_cents=100,
            currency="EUR",
            status="completed",
            created_at=datetime(2026, 5, 22, 0, 0, 0),
        )
        db = MagicMock()
        mock_get_by_iban.return_value = account
        mock_get_account_history.return_value = ([tx], 1)

        result = list_transactions(
            account_id=None,
            account_iban="be12 3456 7890 1234",
            skip=0,
            limit=50,
            db=db,
            current_user=SimpleNamespace(id=uuid.uuid4()),
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, tx.id)
        mock_get_by_iban.assert_called_once_with(db, "be12 3456 7890 1234")
        mock_get_account_history.assert_called_once_with(
            db=db, account_id=account.id, skip=0, limit=50
        )
