from fastapi.testclient import TestClient


class TestUsersAPIGetMe:
    def test_get_me_success(
        self, client: TestClient, authenticated_user_and_token
    ) -> None:
        """Test getting current user info"""
        user = authenticated_user_and_token["user"]
        headers = authenticated_user_and_token["headers"]

        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name

    def test_get_me_unauthenticated(self, client: TestClient) -> None:
        """Test getting user info without authentication"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    def test_get_me_invalid_token(self, client: TestClient) -> None:
        """Test getting user info with invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    def test_get_me_returns_correct_user(
        self, client: TestClient, user_factory
    ) -> None:
        """Test that get_me returns the correct authenticated user"""
        from src.services import auth_service

        user1 = user_factory(email="user1@example.com")
        user_factory(email="user2@example.com")

        # Create session and issue token for user1
        from src.db import SessionLocal

        db = SessionLocal()
        access_token1, _ = auth_service.issue_token_pair(db, user1)
        db.close()

        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token1}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user1@example.com"
        assert data["email"] != "user2@example.com"
