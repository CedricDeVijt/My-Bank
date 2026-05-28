from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.repositories import idempotency_key_repository


class TestIdempotencyKeyRepositoryCreate:
    def test_create_idempotency_key_success(
        self, db_session: Session, user_factory
    ) -> None:
        """Test creating an idempotency key"""
        user = user_factory()
        response_data = '{"status": "success"}'
        status_code = 201

        key = idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="test-key-123",
            method="POST",
            path="/api/v1/transactions",
            response_data=response_data,
            status_code=status_code,
            ttl_seconds=3600,
        )
        db_session.commit()
        db_session.refresh(key)

        assert key.user_id == user.id
        assert key.idempotency_key == "test-key-123"
        assert key.method == "POST"
        assert key.path == "/api/v1/transactions"
        assert key.response_data == response_data
        assert key.status_code == status_code
        assert key.expires_at > datetime.now(UTC).replace(tzinfo=None)

    def test_create_idempotency_key_custom_ttl(
        self, db_session: Session, user_factory
    ) -> None:
        """Test creating an idempotency key with custom TTL"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)

        key = idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="custom-ttl",
            method="POST",
            path="/api/v1/test",
            response_data="{}",
            status_code=200,
            ttl_seconds=7200,  # 2 hours
        )
        db_session.commit()

        # Check that expiration is approximately 2 hours from now
        time_diff = (key.expires_at - now).total_seconds()
        assert 7100 < time_diff < 7300  # Allow some variance


class TestIdempotencyKeyRepositoryGetByKey:
    def test_get_by_key_found_not_expired(
        self, db_session: Session, user_factory
    ) -> None:
        """Test retrieving a valid (non-expired) idempotency key"""
        user = user_factory()

        created = idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="valid-key",
            method="POST",
            path="/api/v1/transactions",
            response_data='{"id": "123"}',
            status_code=201,
        )
        db_session.commit()

        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "valid-key", "POST", "/api/v1/transactions"
        )

        assert result is not None
        assert result.id == created.id
        assert result.idempotency_key == "valid-key"
        assert result.response_data == '{"id": "123"}'

    def test_get_by_key_not_found(self, db_session: Session, user_factory) -> None:
        """Test retrieving a nonexistent idempotency key"""
        user = user_factory()

        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "nonexistent", "POST", "/api/v1/transactions"
        )

        assert result is None

    def test_get_by_key_expired(self, db_session: Session, user_factory) -> None:
        """Test retrieving an expired idempotency key"""
        user = user_factory()

        # Create with very short TTL that's already expired
        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="expired-key",
            method="POST",
            path="/api/v1/transactions",
            response_data="{}",
            status_code=200,
            ttl_seconds=-1,  # Already expired
        )
        db_session.commit()

        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "expired-key", "POST", "/api/v1/transactions"
        )

        assert result is None

    def test_get_by_key_different_user(self, db_session: Session, user_factory) -> None:
        """Test retrieving idempotency key from different user"""
        user1 = user_factory()
        user2 = user_factory()

        idempotency_key_repository.create(
            db=db_session,
            user_id=user1.id,
            idempotency_key="user1-key",
            method="POST",
            path="/api/v1/transactions",
            response_data="{}",
            status_code=200,
        )
        db_session.commit()

        result = idempotency_key_repository.get_by_key(
            db_session, user2.id, "user1-key", "POST", "/api/v1/transactions"
        )

        assert result is None

    def test_get_by_key_different_method(
        self, db_session: Session, user_factory
    ) -> None:
        """Test that method parameter is considered in key retrieval"""
        user = user_factory()

        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="test-key",
            method="POST",
            path="/api/v1/transactions",
            response_data="{}",
            status_code=200,
        )
        db_session.commit()

        # Try to get with different method
        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "test-key", "GET", "/api/v1/transactions"
        )

        assert result is None

    def test_get_by_key_different_path(self, db_session: Session, user_factory) -> None:
        """Test that path parameter is considered in key retrieval"""
        user = user_factory()

        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="test-key",
            method="POST",
            path="/api/v1/transactions",
            response_data="{}",
            status_code=200,
        )
        db_session.commit()

        # Try to get with different path
        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "test-key", "POST", "/api/v1/accounts"
        )

        assert result is None


class TestIdempotencyKeyRepositoryCleanupExpired:
    def test_cleanup_expired_removes_expired_keys(
        self, db_session: Session, user_factory
    ) -> None:
        """Test that cleanup_expired removes expired keys"""
        user = user_factory()

        # Create an already expired key
        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="expired",
            method="POST",
            path="/api/v1/test",
            response_data="{}",
            status_code=200,
            ttl_seconds=-3600,  # Expired 1 hour ago
        )
        # Create a valid key
        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="valid",
            method="POST",
            path="/api/v1/test",
            response_data="{}",
            status_code=200,
            ttl_seconds=3600,  # Expires in 1 hour
        )
        db_session.commit()

        # Run cleanup
        deleted_count = idempotency_key_repository.cleanup_expired(db_session)
        db_session.commit()

        assert deleted_count == 1

        # Verify the valid key still exists
        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "valid", "POST", "/api/v1/test"
        )
        assert result is not None

    def test_cleanup_expired_no_expired_keys(
        self, db_session: Session, user_factory
    ) -> None:
        """Test cleanup_expired when there are no expired keys"""
        user = user_factory()

        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key="valid-key",
            method="POST",
            path="/api/v1/test",
            response_data="{}",
            status_code=200,
            ttl_seconds=3600,
        )
        db_session.commit()

        deleted_count = idempotency_key_repository.cleanup_expired(db_session)
        db_session.commit()

        assert deleted_count == 0

        # Verify the key still exists
        result = idempotency_key_repository.get_by_key(
            db_session, user.id, "valid-key", "POST", "/api/v1/test"
        )
        assert result is not None

    def test_cleanup_expired_multiple_expired(
        self, db_session: Session, user_factory
    ) -> None:
        """Test cleanup_expired with multiple expired keys"""
        user1 = user_factory()
        user2 = user_factory()

        # Create multiple expired keys
        for i in range(5):
            idempotency_key_repository.create(
                db=db_session,
                user_id=user1.id if i % 2 == 0 else user2.id,
                idempotency_key=f"expired-{i}",
                method="POST",
                path="/api/v1/test",
                response_data="{}",
                status_code=200,
                ttl_seconds=-3600,
            )
        db_session.commit()

        deleted_count = idempotency_key_repository.cleanup_expired(db_session)
        db_session.commit()

        assert deleted_count == 5


class TestIdempotencyKeyRepositoryIntegration:
    def test_idempotent_request_detection(
        self, db_session: Session, user_factory
    ) -> None:
        """Test detecting duplicate idempotent requests"""
        user = user_factory()
        key = "duplicate-test"
        method = "POST"
        path = "/api/v1/transactions"

        # First request
        idempotency_key_repository.create(
            db=db_session,
            user_id=user.id,
            idempotency_key=key,
            method=method,
            path=path,
            response_data='{"transaction_id": "123"}',
            status_code=201,
        )
        db_session.commit()

        # Second request with same idempotency key
        result = idempotency_key_repository.get_by_key(
            db_session, user.id, key, method, path
        )

        assert result is not None
        assert result.response_data == '{"transaction_id": "123"}'
        assert result.status_code == 201
