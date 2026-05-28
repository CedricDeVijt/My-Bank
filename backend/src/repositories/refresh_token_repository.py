from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.db.models import RefreshToken


def create(db: Session, data: dict[str, Any]) -> RefreshToken:
    token = RefreshToken(**data)
    db.add(token)
    return token


def get_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    return db.scalars(stmt).first()


def revoke_token(db: Session, token: RefreshToken, revoked_at: datetime) -> None:
    token.revoked_at = revoked_at
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.id == token.id)
        .values(revoked_at=revoked_at)
    )
    db.execute(stmt)


def revoke_family(db: Session, family_id: UUID, revoked_at: datetime) -> None:
    stmt = (
        update(RefreshToken)
        .where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=revoked_at)
    )
    db.execute(stmt)


def revoke_all_for_user(db: Session, user_id: UUID, revoked_at: datetime) -> None:
    stmt = (
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=revoked_at)
    )
    db.execute(stmt)
