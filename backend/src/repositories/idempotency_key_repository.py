import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session
from src.db.models import IdempotencyKey


def get_by_key(
    db: Session, user_id: uuid.UUID, idempotency_key: str, method: str, path: str
) -> IdempotencyKey | None:
    """Get an idempotency key record if it exists and hasn't expired."""
    now = datetime.now(UTC).replace(tzinfo=None)
    stmt = select(IdempotencyKey).where(
        and_(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.idempotency_key == idempotency_key,
            IdempotencyKey.method == method,
            IdempotencyKey.path == path,
            IdempotencyKey.expires_at > now,
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def create(
    db: Session,
    user_id: uuid.UUID,
    idempotency_key: str,
    method: str,
    path: str,
    response_data: str,
    status_code: int,
    ttl_seconds: int = 3600,
) -> IdempotencyKey:
    """Create a new idempotency key record."""
    now = datetime.now(UTC).replace(tzinfo=None)
    expires_at = now + timedelta(seconds=ttl_seconds)

    record = IdempotencyKey(
        user_id=user_id,
        idempotency_key=idempotency_key,
        method=method,
        path=path,
        response_data=response_data,
        status_code=status_code,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(record)
    return record


def cleanup_expired(db: Session) -> int:
    """Delete expired idempotency key records."""
    now = datetime.now(UTC).replace(tzinfo=None)
    stmt = delete(IdempotencyKey).where(IdempotencyKey.expires_at <= now)
    result = db.execute(stmt)
    return result.rowcount or 0
