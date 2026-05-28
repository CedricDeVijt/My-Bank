import uuid
from collections.abc import Generator
from datetime import date
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import get_db
from src.db.base import Base
from src.db.models import Account, User
from src.main import app


@pytest.fixture(scope="session")
def engine() -> Any:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine: Any) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # Ensure each test starts with a clean database.
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(delete(table))
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Test client with overridden database dependency"""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(
    db_session: Session,
) -> Any:
    def _create_user(**overrides: Any) -> User:
        user = User(
            id=overrides.get("id", uuid.uuid4()),
            email=overrides.get("email", f"{uuid.uuid4().hex[:8]}@example.com"),
            first_name=overrides.get("first_name", "Jane"),
            last_name=overrides.get("last_name", "Doe"),
            date_of_birth=overrides.get("date_of_birth", date(1990, 1, 1)),
            hashed_password=overrides.get("hashed_password", "hashed-password"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def account_factory(
    db_session: Session,
) -> Any:
    def _create_account(**overrides: Any) -> Account:
        default_digits = str(uuid.uuid4().int)[:12]
        account = Account(
            id=overrides.get("id", uuid.uuid4()),
            account_number=overrides.get("account_number", default_digits),
            iban=overrides.get("iban", f"BE12{default_digits}"),
            type=overrides.get("type", "checking"),
            currency=overrides.get("currency", "EUR"),
            balance_cents=overrides.get("balance_cents", 0),
            status=overrides.get("status", "active"),
            created_at=overrides.get("created_at", date.today()),
            account_holder_id=overrides["account_holder_id"],
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        return account

    return _create_account


@pytest.fixture
def authenticated_user_and_token(db_session: Session, user_factory) -> Any:
    """Create an authenticated user with valid tokens"""
    from src.services import auth_service

    user = user_factory()
    access_token, refresh_token = auth_service.issue_token_pair(db_session, user)
    db_session.commit()

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "headers": {"Authorization": f"Bearer {access_token}"},
    }
