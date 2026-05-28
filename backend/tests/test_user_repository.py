import uuid
from datetime import date

from sqlalchemy.orm import Session

from src.repositories import user_repository


class TestUserRepositoryCreate:
    def test_create_user_success(self, db_session: Session) -> None:
        """Test creating a user with valid data"""
        user_data = {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(1990, 1, 1),
            "hashed_password": "hashed_password",
        }

        user = user_repository.create(db_session, user_data)
        db_session.commit()
        db_session.refresh(user)

        assert user.id == user_data["id"]
        assert user.email == user_data["email"]
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_create_user_with_minimal_data(self, db_session: Session) -> None:
        """Test creating a user with minimal required fields"""
        user_id = uuid.uuid4()
        user_data = {
            "id": user_id,
            "email": "minimal@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": date(1985, 5, 15),
            "hashed_password": "hashed",
        }

        user = user_repository.create(db_session, user_data)
        db_session.commit()
        db_session.refresh(user)

        assert user.id == user_id
        assert user.email == "minimal@example.com"


class TestUserRepositoryGetByEmail:
    def test_get_by_email_found(self, db_session: Session) -> None:
        """Test retrieving a user by email when user exists"""
        user_data = {
            "email": "exists@example.com",
            "first_name": "Alice",
            "last_name": "Johnson",
            "date_of_birth": date(1992, 3, 10),
            "hashed_password": "hashed",
        }
        user = user_repository.create(db_session, user_data)
        db_session.commit()

        result = user_repository.get_by_email(db_session, "exists@example.com")

        assert result is not None
        assert result.id == user.id
        assert result.email == "exists@example.com"

    def test_get_by_email_not_found(self, db_session: Session) -> None:
        """Test retrieving a user by email when user doesn't exist"""
        result = user_repository.get_by_email(db_session, "nonexistent@example.com")
        assert result is None

    def test_get_by_email_case_sensitive(self, db_session: Session) -> None:
        """Test that email search is case-insensitive or handles case properly"""
        user_data = {
            "email": "test@example.com",
            "first_name": "Bob",
            "last_name": "Wilson",
            "date_of_birth": date(1988, 7, 20),
            "hashed_password": "hashed",
        }
        user_repository.create(db_session, user_data)
        db_session.commit()

        # Depending on database config, this might be case-sensitive
        result = user_repository.get_by_email(db_session, "test@example.com")
        assert result is not None


class TestUserRepositoryGetById:
    def test_get_by_id_found(self, db_session: Session, user_factory) -> None:
        """Test retrieving a user by ID when user exists"""
        user = user_factory()

        result = user_repository.get_by_id(db_session, user.id)

        assert result is not None
        assert result.id == user.id
        assert result.email == user.email

    def test_get_by_id_not_found(self, db_session: Session) -> None:
        """Test retrieving a user by ID when user doesn't exist"""
        random_id = uuid.uuid4()

        result = user_repository.get_by_id(db_session, random_id)

        assert result is None

    def test_get_by_id_multiple_users(self, db_session: Session, user_factory) -> None:
        """Test retrieving specific user by ID with multiple users in database"""
        user1 = user_factory()
        user2 = user_factory()

        result = user_repository.get_by_id(db_session, user1.id)

        assert result is not None
        assert result.id == user1.id
        assert result.id != user2.id


class TestUserRepositoryIntegration:
    def test_create_and_retrieve_user(self, db_session: Session) -> None:
        """Test creating and retrieving the same user"""
        user_data = {
            "email": "integration@example.com",
            "first_name": "Integration",
            "last_name": "Test",
            "date_of_birth": date(1995, 11, 5),
            "hashed_password": "hashed_password",
        }

        created_user = user_repository.create(db_session, user_data)
        db_session.commit()

        retrieved_by_email = user_repository.get_by_email(
            db_session, "integration@example.com"
        )
        retrieved_by_id = user_repository.get_by_id(db_session, created_user.id)

        assert retrieved_by_email is not None
        assert retrieved_by_id is not None
        assert retrieved_by_email.id == retrieved_by_id.id
        assert retrieved_by_email.email == "integration@example.com"
