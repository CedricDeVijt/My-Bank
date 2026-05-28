import time

import pytest

from src.core.config import settings
from src.core.security import (
    InvalidTokenError,
    TokenExpiredError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password(self) -> None:
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self) -> None:
        """Test password verification with correct password"""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed)

    def test_verify_password_incorrect(self) -> None:
        """Test password verification fails with incorrect password"""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert not verify_password("WrongPassword123!", hashed)

    def test_hash_password_idempotency(self) -> None:
        """Test that hashing same password produces different hashes"""
        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (due to random salt)
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestTokenHashing:
    def test_hash_token(self) -> None:
        """Test token hashing"""
        token = "some_jwt_token_here"
        hashed = hash_token(token)

        assert hashed != token
        assert len(hashed) == 64  # SHA256 produces 64 hex characters

    def test_hash_token_idempotency(self) -> None:
        """Test that hashing same token produces same hash"""
        token = "some_jwt_token_here"
        hash1 = hash_token(token)
        hash2 = hash_token(token)

        assert hash1 == hash2

    def test_hash_token_different_tokens(self) -> None:
        """Test that different tokens produce different hashes"""
        token1 = "token_one"
        token2 = "token_two"

        hash1 = hash_token(token1)
        hash2 = hash_token(token2)

        assert hash1 != hash2


class TestCreateAccessToken:
    def test_create_access_token(self) -> None:
        """Test creating an access token"""
        data = {"sub": "user-id", "email": "test@example.com"}
        token = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,
        )

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT should have 3 parts separated by dots
        assert token.count(".") == 2

    def test_create_access_token_payload(self) -> None:
        """Test that access token contains correct payload"""
        data = {"sub": "user-id", "email": "test@example.com"}
        token = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,
        )

        payload = decode_token(token, settings.jwt_secret_key)
        assert payload["sub"] == "user-id"
        assert payload["email"] == "test@example.com"
        assert payload["token_use"] == "access"

    def test_create_access_token_different_expiry(self) -> None:
        """Test creating access tokens with different expiry times"""
        data = {"sub": "user-id"}

        token1 = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,  # 1 hour
        )
        token2 = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=7200,  # 2 hours
        )

        # Tokens should be different
        assert token1 != token2

        payload1 = decode_token(token1, settings.jwt_secret_key)
        payload2 = decode_token(token2, settings.jwt_secret_key)

        # Expiry should be different (payload2 should expire later)
        assert payload1["exp"] < payload2["exp"]


class TestCreateRefreshToken:
    def test_create_refresh_token(self) -> None:
        """Test creating a refresh token"""
        data = {"sub": "user-id", "family_id": "family-123"}
        token = create_refresh_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=604800,  # 1 week
        )

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2

    def test_create_refresh_token_payload(self) -> None:
        """Test that refresh token contains correct payload"""
        data = {"sub": "user-id", "family_id": "family-123"}
        token = create_refresh_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=604800,
        )

        payload = decode_token(token, settings.jwt_secret_key)
        assert payload["sub"] == "user-id"
        assert payload["family_id"] == "family-123"
        assert payload["token_use"] == "refresh"


class TestDecodeToken:
    def test_decode_token_success(self) -> None:
        """Test successful token decoding"""
        data = {"sub": "user-id", "email": "test@example.com"}
        token = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,
        )

        payload = decode_token(token, settings.jwt_secret_key)

        assert payload["sub"] == "user-id"
        assert payload["email"] == "test@example.com"

    def test_decode_token_invalid_signature(self) -> None:
        """Test decoding fails with invalid signature"""
        data = {"sub": "user-id"}
        token = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,
        )

        with pytest.raises(InvalidTokenError):
            decode_token(token, "wrong-secret-key")

    def test_decode_token_malformed(self) -> None:
        """Test decoding fails with malformed token"""
        with pytest.raises(InvalidTokenError):
            decode_token("not.a.valid.jwt", settings.jwt_secret_key)

    def test_decode_token_expired(self) -> None:
        """Test decoding fails with expired token"""
        data = {"sub": "user-id"}
        token = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=0,  # Expires immediately
        )

        # Wait a moment to ensure token has expired
        time.sleep(0.1)

        with pytest.raises(TokenExpiredError):
            decode_token(token, settings.jwt_secret_key)

    def test_decode_token_missing_required_fields(self) -> None:
        """Test decoding token with missing required fields"""
        # Create token without standard fields

        import jwt

        payload = {"custom": "data"}  # Missing "sub" and other standard fields
        token = jwt.encode(payload, settings.jwt_secret_key, settings.jwt_algorithm)

        # Decoding should work even with missing fields
        result = decode_token(token, settings.jwt_secret_key)
        assert result["custom"] == "data"


class TestTokenIntegration:
    def test_create_and_decode_access_token(self) -> None:
        """Test full cycle of creating and decoding access token"""
        original_data = {"sub": "user-123", "email": "user@example.com"}

        token = create_access_token(
            data=original_data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,
        )

        decoded = decode_token(token, settings.jwt_secret_key)

        assert decoded["sub"] == original_data["sub"]
        assert decoded["email"] == original_data["email"]
        assert decoded["token_use"] == "access"

    def test_create_and_decode_refresh_token(self) -> None:
        """Test full cycle of creating and decoding refresh token"""
        original_data = {"sub": "user-123", "family_id": "family-456"}

        token = create_refresh_token(
            data=original_data,
            secret_key=settings.jwt_secret_key,
            expires_in=604800,
        )

        decoded = decode_token(token, settings.jwt_secret_key)

        assert decoded["sub"] == original_data["sub"]
        assert decoded["family_id"] == original_data["family_id"]
        assert decoded["token_use"] == "refresh"

    def test_different_algorithms_fail(self) -> None:
        """Test that using different algorithms fails"""
        data = {"sub": "user-id"}

        # Create with HS256
        token = create_access_token(
            data=data,
            secret_key=settings.jwt_secret_key,
            expires_in=3600,
            algorithm="HS256",
        )

        # Trying to decode with HS512 should fail
        with pytest.raises(InvalidTokenError):
            decode_token(token, settings.jwt_secret_key, algorithm="HS512")
