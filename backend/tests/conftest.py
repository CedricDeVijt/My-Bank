import uuid
from collections.abc import Generator
from datetime import date
from typing import Any

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.db.models import Account, User


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
