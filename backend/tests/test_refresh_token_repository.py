import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.db.models import RefreshToken
from src.repositories import refresh_token_repository


class TestRefreshTokenRepositoryCreate:
    def test_create_token_success(self, db_session: Session, user_factory) -> None:
        """Test creating a refresh token"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        family_id = uuid.uuid4()
        token_hash = "hashed_token_value"

        token = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": token_hash,
                "family_id": family_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        db_session.commit()
        db_session.refresh(token)

        assert token.user_id == user.id
        assert token.token_hash == token_hash
        assert token.family_id == family_id
        assert token.revoked_at is None

    def test_create_multiple_tokens_same_family(
        self, db_session: Session, user_factory
    ) -> None:
        """Test creating multiple tokens in the same family"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        family_id = uuid.uuid4()

        token1 = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "hash1",
                "family_id": family_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        token2 = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "hash2",
                "family_id": family_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        db_session.commit()

        assert token1.family_id == token2.family_id
        assert token1.token_hash != token2.token_hash


class TestRefreshTokenRepositoryGetByHash:
    def test_get_by_hash_found(self, db_session: Session, user_factory) -> None:
        """Test retrieving a token by hash when it exists"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        token_hash = "test_token_hash"

        created = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": token_hash,
                "family_id": uuid.uuid4(),
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        db_session.commit()

        result = refresh_token_repository.get_by_hash(db_session, token_hash)

        assert result is not None
        assert result.id == created.id
        assert result.token_hash == token_hash

    def test_get_by_hash_not_found(self, db_session: Session) -> None:
        """Test retrieving a token by hash when it doesn't exist"""
        result = refresh_token_repository.get_by_hash(db_session, "nonexistent_hash")

        assert result is None


class TestRefreshTokenRepositoryRevokeToken:
    def test_revoke_token_success(self, db_session: Session, user_factory) -> None:
        """Test revoking a single token"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)

        token = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "revoke_test",
                "family_id": uuid.uuid4(),
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        db_session.commit()

        revoked_at = datetime.now(UTC).replace(tzinfo=None)
        refresh_token_repository.revoke_token(db_session, token, revoked_at)
        db_session.commit()

        # Retrieve token to verify revocation
        result = db_session.query(RefreshToken).filter_by(id=token.id).first()
        assert result.revoked_at is not None
        assert result.revoked_at == revoked_at

    def test_revoke_token_doesnt_affect_others(
        self, db_session: Session, user_factory
    ) -> None:
        """Test that revoking one token doesn't affect others"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        family_id = uuid.uuid4()

        token1 = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "token1",
                "family_id": family_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        token2 = refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "token2",
                "family_id": family_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        db_session.commit()

        revoked_at = datetime.now(UTC).replace(tzinfo=None)
        refresh_token_repository.revoke_token(db_session, token1, revoked_at)
        db_session.commit()

        result1 = db_session.query(RefreshToken).filter_by(id=token1.id).first()
        result2 = db_session.query(RefreshToken).filter_by(id=token2.id).first()

        assert result1.revoked_at is not None
        assert result2.revoked_at is None


class TestRefreshTokenRepositoryRevokeFamily:
    def test_revoke_family_success(self, db_session: Session, user_factory) -> None:
        """Test revoking all tokens in a family"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        family_id = uuid.uuid4()

        # Create multiple tokens in same family
        for i in range(3):
            refresh_token_repository.create(
                db_session,
                data={
                    "user_id": user.id,
                    "token_hash": f"token{i}",
                    "family_id": family_id,
                    "created_at": now,
                    "expires_at": now + timedelta(hours=1),
                },
            )
        db_session.commit()

        revoked_at = datetime.now(UTC).replace(tzinfo=None)
        refresh_token_repository.revoke_family(db_session, family_id, revoked_at)
        db_session.commit()

        # Check all tokens in family are revoked
        tokens = db_session.query(RefreshToken).filter_by(family_id=family_id).all()
        assert len(tokens) == 3
        for token in tokens:
            assert token.revoked_at is not None

    def test_revoke_family_doesnt_affect_other_families(
        self, db_session: Session, user_factory
    ) -> None:
        """Test that revoking one family doesn't affect others"""
        user = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        family1_id = uuid.uuid4()
        family2_id = uuid.uuid4()

        # Create tokens in two different families
        refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "family1_token",
                "family_id": family1_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        refresh_token_repository.create(
            db_session,
            data={
                "user_id": user.id,
                "token_hash": "family2_token",
                "family_id": family2_id,
                "created_at": now,
                "expires_at": now + timedelta(hours=1),
            },
        )
        db_session.commit()

        revoked_at = datetime.now(UTC).replace(tzinfo=None)
        refresh_token_repository.revoke_family(db_session, family1_id, revoked_at)
        db_session.commit()

        family1_tokens = (
            db_session.query(RefreshToken).filter_by(family_id=family1_id).all()
        )
        family2_tokens = (
            db_session.query(RefreshToken).filter_by(family_id=family2_id).all()
        )

        assert all(t.revoked_at is not None for t in family1_tokens)
        assert all(t.revoked_at is None for t in family2_tokens)


class TestRefreshTokenRepositoryRevokeAllForUser:
    def test_revoke_all_for_user_success(
        self, db_session: Session, user_factory
    ) -> None:
        """Test revoking all tokens for a user"""
        user1 = user_factory()
        user2 = user_factory()
        now = datetime.now(UTC).replace(tzinfo=None)

        # Create tokens for both users
        for i in range(2):
            refresh_token_repository.create(
                db_session,
                data={
                    "user_id": user1.id,
                    "token_hash": f"user1_token{i}",
                    "family_id": uuid.uuid4(),
                    "created_at": now,
                    "expires_at": now + timedelta(hours=1),
                },
            )
            refresh_token_repository.create(
                db_session,
                data={
                    "user_id": user2.id,
                    "token_hash": f"user2_token{i}",
                    "family_id": uuid.uuid4(),
                    "created_at": now,
                    "expires_at": now + timedelta(hours=1),
                },
            )
        db_session.commit()

        revoked_at = datetime.now(UTC).replace(tzinfo=None)
        refresh_token_repository.revoke_all_for_user(db_session, user1.id, revoked_at)
        db_session.commit()

        # Check user1's tokens are revoked
        user1_tokens = db_session.query(RefreshToken).filter_by(user_id=user1.id).all()
        user2_tokens = db_session.query(RefreshToken).filter_by(user_id=user2.id).all()

        assert all(t.revoked_at is not None for t in user1_tokens)
        assert all(t.revoked_at is None for t in user2_tokens)
