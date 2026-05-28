from collections.abc import Generator
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from src.api.dependencies import get_current_user
from src.api.v1.accounts import router
from src.db import get_db


def test_list_accounts_masks_sensitive_fields(
    db_session: Any,
    user_factory: Any,
    account_factory: Any,
    engine: Any,
) -> None:
    user = user_factory(email="api-owner@example.com")
    account_factory(
        account_holder_id=user.id,
        account_number="123456789012",
        iban="BE12123456789012",
        balance_cents=1200,
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Generator[Any, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user.id)

    with TestClient(app) as client:
        response = client.get("/api/v1/accounts")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["accounts"]) == 1
    assert payload["accounts"][0]["account_number"] == "****9012"
    assert payload["accounts"][0]["iban"] == "BE12****9012"


def test_create_account_returns_unmasked_fields(engine: Any, user_factory: Any) -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    user = user_factory(email="api-create@example.com")

    def override_get_db() -> Generator[Any, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user.id)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/accounts",
            json={"type": "checking", "currency": "EUR"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["account_number"][:4] != "****"
    assert payload["iban"].startswith("BE")
    assert payload["currency"] == "EUR"
    assert payload["type"] == "checking"
