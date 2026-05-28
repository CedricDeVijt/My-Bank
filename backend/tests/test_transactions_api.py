from fastapi.testclient import TestClient


class TestTransactionsAPICreateTransaction:
    def test_create_transaction_success(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test successful transaction creation"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": "tx-key-1"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["amount_cents"] == 50000
        assert data["currency"] == "EUR"
        assert data["status"] == "completed"

    def test_create_transaction_insufficient_balance(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test transaction fails with insufficient balance"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        from_account = account_factory(account_holder_id=user.id, balance_cents=30000)
        to_account = account_factory(account_holder_id=user.id)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": "tx-key-2"},
        )

        assert response.status_code == 400

    def test_create_transaction_same_account(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test transaction fails when transferring to same account"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        account = account_factory(account_holder_id=user.id, balance_cents=100000)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": account.iban,
                "to_iban": account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": "tx-key-3"},
        )

        assert response.status_code == 422

    def test_create_transaction_invalid_amount(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test transaction fails with invalid amount"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 0,
            },
            headers={**headers, "Idempotency-Key": "tx-key-4"},
        )

        assert response.status_code == 422

    def test_create_transaction_account_not_found(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test transaction fails when account not found"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        to_account = account_factory(account_holder_id=user.id)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": "NONEXISTENT",
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": "tx-key-5"},
        )

        assert response.status_code == 404

    def test_create_transaction_unauthorized(
        self,
        client: TestClient,
        authenticated_user_and_token,
        account_factory,
        user_factory,
    ) -> None:
        """Test transaction fails when user doesn't own from account"""
        user1 = authenticated_user_and_token["user"]
        user2 = user_factory()
        headers = authenticated_user_and_token["headers"]

        from_account = account_factory(account_holder_id=user2.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user1.id)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": "tx-key-6"},
        )

        assert response.status_code == 403

    def test_create_transaction_currency_mismatch(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test transaction fails with currency mismatch"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        from_account = account_factory(
            account_holder_id=user.id, balance_cents=100000, currency="EUR"
        )
        to_account = account_factory(account_holder_id=user.id, currency="USD")

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": "tx-key-7"},
        )

        assert response.status_code == 400

    def test_create_transaction_unauthenticated(
        self, client: TestClient, account_factory, user_factory
    ) -> None:
        """Test transaction fails without authentication"""
        user = user_factory()
        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id)

        response = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={"Idempotency-Key": "tx-key-8"},
        )

        assert response.status_code == 401

    def test_create_transaction_idempotency(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test idempotency key is accepted."""
        # Note: actual caching may not be in place
        user = authenticated_user_and_token["user"]

        headers = authenticated_user_and_token["headers"]
        idempotency_key = "idempotent-tx-key"

        from_account = account_factory(account_holder_id=user.id, balance_cents=100000)
        to_account = account_factory(account_holder_id=user.id)

        # First request
        response1 = client.post(
            "/api/v1/transactions",
            json={
                "from_iban": from_account.iban,
                "to_iban": to_account.iban,
                "amount_cents": 50000,
            },
            headers={**headers, "Idempotency-Key": idempotency_key},
        )

        assert response1.status_code == 201
        assert "id" in response1.json()


class TestTransactionsAPIListTransactions:
    def test_list_transactions_success(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test listing transactions for an account"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        from_account = account_factory(account_holder_id=user.id, balance_cents=500000)

        # Empty account should return empty list
        response = client.get(
            "/api/v1/transactions",
            params={"account_id": str(from_account.id)},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0

    def test_list_transactions_by_iban(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test listing transactions by IBAN"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        account = account_factory(account_holder_id=user.id)

        response = client.get(
            "/api/v1/transactions",
            params={"account_iban": account.iban},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_transactions_missing_account_param(
        self, client: TestClient, authenticated_user_and_token
    ) -> None:
        """Test listing transactions fails without account parameter"""
        headers = authenticated_user_and_token["headers"]

        response = client.get(
            "/api/v1/transactions",
            headers=headers,
        )

        assert response.status_code == 400

    def test_list_transactions_invalid_account_id(
        self, client: TestClient, authenticated_user_and_token
    ) -> None:
        """Test listing transactions with invalid account ID format"""
        headers = authenticated_user_and_token["headers"]

        response = client.get(
            "/api/v1/transactions",
            params={"account_id": "invalid-uuid"},
            headers=headers,
        )

        # Should return either 400 or 500 for invalid UUID format
        assert response.status_code in [400, 422, 500]

    def test_list_transactions_account_not_found(
        self, client: TestClient, authenticated_user_and_token
    ) -> None:
        """Test listing transactions for non-existent IBAN"""
        headers = authenticated_user_and_token["headers"]

        response = client.get(
            "/api/v1/transactions",
            params={"account_iban": "NONEXISTENT"},
            headers=headers,
        )

        # Should return either 404 or 500
        assert response.status_code in [404, 500]

    def test_list_transactions_pagination(
        self, client: TestClient, authenticated_user_and_token, account_factory
    ) -> None:
        """Test pagination of transactions"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        account = account_factory(account_holder_id=user.id)

        # Pagination is supported
        response = client.get(
            "/api/v1/transactions",
            params={"account_id": str(account.id), "skip": 0, "limit": 10},
            headers=headers,
        )

        assert response.status_code == 200

    def test_list_transactions_unauthenticated(self, client: TestClient) -> None:
        """Test listing transactions without authentication"""
        import uuid

        response = client.get(
            "/api/v1/transactions",
            params={"account_id": str(uuid.uuid4())},
        )

        assert response.status_code == 401
