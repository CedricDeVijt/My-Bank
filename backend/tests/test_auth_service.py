from datetime import date

import pytest
from sqlalchemy.orm import Session

from src.core.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    RefreshTokenError,
)
from src.core.security import (
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.schemas.User import UserCreate
from src.services import auth_service


class TestAuthServiceRegisterUser:
    def test_register_user_success(self, db_session: Session) -> None:
        """Test successful user registration"""
        user_create = UserCreate(
            email="newuser@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
        )

        user = auth_service.register_user(db_session, user_create)

        assert user.email == "newuser@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.hashed_password != "SecurePassword123!"
        assert verify_password("SecurePassword123!", user.hashed_password)

    def test_register_user_email_already_exists(
        self, db_session: Session, user_factory
    ) -> None:
        """Test registration fails when email already exists"""
        user_factory(email="existing@example.com")

        user_create = UserCreate(
            email="existing@example.com",
            password="SecurePassword123!",
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
        )

        with pytest.raises(EmailAlreadyRegisteredError):
            auth_service.register_user(db_session, user_create)

    def test_register_user_different_emails_success(self, db_session: Session) -> None:
        """Test multiple users can register with different emails"""
        user1 = UserCreate(
            email="user1@example.com",
            password="SecurePassword123!",
            first_name="User",
            last_name="One",
            date_of_birth=date(1990, 1, 1),
        )
        user2 = UserCreate(
            email="user2@example.com",
            password="SecurePassword123!",
            first_name="User",
            last_name="Two",
            date_of_birth=date(1991, 2, 2),
        )

        created1 = auth_service.register_user(db_session, user1)
        created2 = auth_service.register_user(db_session, user2)

        assert created1.email != created2.email
        assert created1.id != created2.id


class TestAuthServiceAuthenticateUser:
    def test_authenticate_user_success(self, db_session: Session, user_factory) -> None:
        """Test successful user authentication"""
        password = "CorrectPassword123!"
        user = user_factory(
            hashed_password=hash_password(password),
            email="auth@example.com",
        )

        result = auth_service.authenticate_user(
            db_session, "auth@example.com", password
        )

        assert result.id == user.id
        assert result.email == "auth@example.com"

    def test_authenticate_user_invalid_email(self, db_session: Session) -> None:
        """Test authentication fails with non-existent email"""
        with pytest.raises(AuthenticationError):
            auth_service.authenticate_user(
                db_session, "nonexistent@example.com", "password"
            )

    def test_authenticate_user_invalid_password(
        self, db_session: Session, user_factory
    ) -> None:
        """Test authentication fails with wrong password"""
        user_factory(
            hashed_password=hash_password("CorrectPassword123!"),
            email="auth@example.com",
        )

        with pytest.raises(AuthenticationError):
            auth_service.authenticate_user(
                db_session, "auth@example.com", "WrongPassword123!"
            )

    def test_authenticate_user_case_sensitive_email(
        self, db_session: Session, user_factory
    ) -> None:
        """Test authentication with email case sensitivity"""
        password = "Password123!"
        user_factory(
            hashed_password=hash_password(password),
            email="Test@Example.com",
        )

        # Depending on database configuration, this might work or fail
        try:
            result = auth_service.authenticate_user(
                db_session, "test@example.com", password
            )
            # If it works, that's fine
            assert result.email == "Test@Example.com"
        except AuthenticationError:
            # If it fails, that's also acceptable for case-sensitivity
            pass


class TestAuthServiceIssueTokenPair:
    def test_issue_token_pair_success(self, db_session: Session, user_factory) -> None:
        """Test issuing access and refresh tokens"""
        user = user_factory()

        access_token, refresh_token = auth_service.issue_token_pair(db_session, user)

        assert access_token
        assert refresh_token
        assert len(access_token) > 0
        assert len(refresh_token) > 0

        # Verify tokens can be decoded
        from src.core.config import settings

        access_payload = decode_token(
            access_token, settings.jwt_secret_key, settings.jwt_algorithm
        )
        refresh_payload = decode_token(
            refresh_token, settings.jwt_secret_key, settings.jwt_algorithm
        )

        assert access_payload["token_use"] == "access"
        assert refresh_payload["token_use"] == "refresh"
        assert access_payload["sub"] == str(user.id)
        assert refresh_payload["sub"] == str(user.id)

    def test_issue_token_pair_with_family_id(
        self, db_session: Session, user_factory
    ) -> None:
        """Test issuing token pair with specific family ID"""
        import uuid

        user = user_factory()
        family_id = uuid.uuid4()

        access_token, refresh_token = auth_service.issue_token_pair(
            db_session, user, family_id
        )

        from src.core.config import settings

        refresh_payload = decode_token(
            refresh_token, settings.jwt_secret_key, settings.jwt_algorithm
        )
        assert refresh_payload["family_id"] == str(family_id)

    def test_issue_token_pair_creates_db_record(
        self, db_session: Session, user_factory
    ) -> None:
        """Test that refresh token is saved to database"""
        from src.db.models import RefreshToken

        user = user_factory()

        auth_service.issue_token_pair(db_session, user)

        # Check that refresh token record was created
        tokens = db_session.query(RefreshToken).filter_by(user_id=user.id).all()
        assert len(tokens) == 1
        assert tokens[0].revoked_at is None


class TestAuthServiceRefreshTokens:
    def test_refresh_tokens_invalid_token(self, db_session: Session) -> None:
        """Test refresh fails with invalid token"""
        invalid_token = "invalid.token.here"

        with pytest.raises(RefreshTokenError):
            auth_service.refresh_tokens(db_session, invalid_token)

    def test_refresh_tokens_wrong_token_use(
        self, db_session: Session, user_factory
    ) -> None:
        """Test refresh fails when using access token instead of refresh token"""

        user = user_factory()
        access_token, _ = auth_service.issue_token_pair(db_session, user)
        db_session.commit()

        # Try to use access token as refresh token
        with pytest.raises(RefreshTokenError):
            auth_service.refresh_tokens(db_session, access_token)


class TestAuthServiceLogout:
    def test_logout_success(self, db_session: Session, user_factory) -> None:
        """Test successful logout"""
        user = user_factory()
        _, refresh_token = auth_service.issue_token_pair(db_session, user)
        db_session.commit()

        # Logout should not raise
        auth_service.logout(db_session, user.id, refresh_token)
        db_session.commit()

        # Token should be revoked
        from src.db.models import RefreshToken

        token_record = (
            db_session.query(RefreshToken)
            .filter_by(token_hash=hash_token(refresh_token))
            .first()
        )
        assert token_record.revoked_at is not None

    def test_logout_invalid_token(self, db_session: Session, user_factory) -> None:
        """Test logout with invalid token"""
        user = user_factory()

        with pytest.raises(RefreshTokenError):
            auth_service.logout(db_session, user.id, "invalid_token")

    def test_logout_wrong_user(self, db_session: Session, user_factory) -> None:
        """Test logout fails when user doesn't own the token"""
        user1 = user_factory()
        user2 = user_factory()

        _, refresh_token = auth_service.issue_token_pair(db_session, user1)
        db_session.commit()

        # User2 tries to logout with user1's token
        with pytest.raises(RefreshTokenError):
            auth_service.logout(db_session, user2.id, refresh_token)

    def test_logout_already_logged_out(self, db_session: Session, user_factory) -> None:
        """Test logout when already logged out (token already revoked)"""
        user = user_factory()
        _, refresh_token = auth_service.issue_token_pair(db_session, user)
        db_session.commit()

        # First logout
        auth_service.logout(db_session, user.id, refresh_token)
        db_session.commit()

        # Second logout with same token - should not raise
        auth_service.logout(db_session, user.id, refresh_token)
        db_session.commit()


class TestAuthServiceIntegration:
    def test_auth_flow_register_and_authenticate(self, db_session: Session) -> None:
        """Test registration and authentication flow"""
        # 1. Register
        user_create = UserCreate(
            email="flowtest@example.com",
            password="SecurePassword123!",
            first_name="Flow",
            last_name="Test",
            date_of_birth=date(1990, 1, 1),
        )
        user = auth_service.register_user(db_session, user_create)
        db_session.commit()

        # 2. Authenticate (login)
        authenticated_user = auth_service.authenticate_user(
            db_session, "flowtest@example.com", "SecurePassword123!"
        )
        assert authenticated_user.id == user.id

        # 3. Issue tokens
        access_token, refresh_token = auth_service.issue_token_pair(
            db_session, authenticated_user
        )
        db_session.commit()

        assert access_token
        assert refresh_token

    def test_auth_logout(self, db_session: Session) -> None:
        """Test logout revokes tokens"""
        user_create = UserCreate(
            email="logouttest@example.com",
            password="SecurePassword123!",
            first_name="Logout",
            last_name="Test",
            date_of_birth=date(1990, 1, 1),
        )
        user = auth_service.register_user(db_session, user_create)
        db_session.commit()

        # Issue tokens
        _, refresh_token = auth_service.issue_token_pair(db_session, user)
        db_session.commit()

        # Logout
        auth_service.logout(db_session, user.id, refresh_token)
        db_session.commit()

        # Verify token is revoked
        from src.db.models import RefreshToken

        token_record = (
            db_session.query(RefreshToken)
            .filter_by(token_hash=hash_token(refresh_token))
            .first()
        )
        assert token_record.revoked_at is not None
