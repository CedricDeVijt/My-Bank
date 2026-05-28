from fastapi.testclient import TestClient


class TestAuthAPIRegister:
    def test_register_success(self, client: TestClient) -> None:
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
            },
            headers={"Idempotency-Key": "test-key-1"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    def test_register_duplicate_email(self, client: TestClient, user_factory) -> None:
        """Test registration fails with duplicate email"""
        user_factory(email="existing@example.com")

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "SecurePassword123!",
                "first_name": "Jane",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
            },
            headers={"Idempotency-Key": "test-key-2"},
        )

        assert response.status_code == 409

    def test_register_invalid_email(self, client: TestClient) -> None:
        """Test registration fails with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
            },
            headers={"Idempotency-Key": "test-key-3"},
        )

        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient) -> None:
        """Test registration fails with short password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "short",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
            },
            headers={"Idempotency-Key": "test-key-4"},
        )

        assert response.status_code == 422


class TestAuthAPILogin:
    def test_login_success(self, client: TestClient, user_factory) -> None:
        """Test successful login"""
        from src.core.security import hash_password

        user_factory(
            email="login@example.com",
            hashed_password=hash_password("CorrectPassword123!"),
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "CorrectPassword123!",
            },
            headers={"Idempotency-Key": "login-key-1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["access_token_expires_in"] > 0
        assert data["refresh_token_expires_in"] > 0

    def test_login_invalid_email(self, client: TestClient) -> None:
        """Test login fails with non-existent email"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123!",
            },
            headers={"Idempotency-Key": "login-key-2"},
        )

        assert response.status_code == 401

    def test_login_invalid_password(self, client: TestClient, user_factory) -> None:
        """Test login fails with wrong password"""
        from src.core.security import hash_password

        user_factory(
            email="login@example.com",
            hashed_password=hash_password("CorrectPassword123!"),
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "WrongPassword123!",
            },
            headers={"Idempotency-Key": "login-key-3"},
        )

        assert response.status_code == 401


class TestAuthAPIRefreshToken:
    def test_refresh_token_invalid_token(self, client: TestClient) -> None:
        """Test refresh fails with invalid token"""
        response = client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": "invalid.token.here"},
            headers={"Idempotency-Key": "refresh-key-2"},
        )

        assert response.status_code == 401


class TestAuthAPILogout:
    def test_logout_success(
        self, client: TestClient, authenticated_user_and_token
    ) -> None:
        """Test successful logout"""
        refresh_token = authenticated_user_and_token["refresh_token"]
        headers = authenticated_user_and_token["headers"]

        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={**headers, "Idempotency-Key": "logout-key-1"},
        )

        assert response.status_code == 204

    def test_logout_unauthorized(self, client: TestClient) -> None:
        """Test logout fails without authentication"""
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "any-token"},
            headers={"Idempotency-Key": "logout-key-2"},
        )

        assert response.status_code == 401

    def test_logout_invalid_token(
        self, client: TestClient, authenticated_user_and_token
    ) -> None:
        """Test logout with invalid token"""
        headers = authenticated_user_and_token["headers"]

        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "invalid.token.here"},
            headers={**headers, "Idempotency-Key": "logout-key-3"},
        )

        assert response.status_code == 401
