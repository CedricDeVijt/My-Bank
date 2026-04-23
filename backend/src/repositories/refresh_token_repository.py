from datetime import datetime
from typing import cast
from uuid import UUID

from sqlalchemy.orm import Session
from src.db.models import RefreshToken


def create(db: Session, data: dict) -> RefreshToken:
    token = RefreshToken(**data)
    db.add(token)
    return token


def get_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    return cast(
        RefreshToken | None,
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first(),
    )


def revoke_token(db: Session, token: RefreshToken, revoked_at: datetime) -> None:
    token.revoked_at = revoked_at
    db.query(RefreshToken).filter(RefreshToken.id == token.id).update(
        {RefreshToken.revoked_at: revoked_at}, synchronize_session=False
    )


def revoke_family(db: Session, family_id: UUID, revoked_at: datetime) -> None:
    (
        db.query(RefreshToken)
        .filter(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .update({RefreshToken.revoked_at: revoked_at}, synchronize_session=False)
    )


def revoke_all_for_user(db: Session, user_id: UUID, revoked_at: datetime) -> None:
    (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .update({RefreshToken.revoked_at: revoked_at}, synchronize_session=False)
    )
