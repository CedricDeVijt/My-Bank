import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Base


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    from_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account.id"), nullable=False
    )
    to_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account.id"), nullable=False
    )

    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False)

    # Status: pending, completed, failed
    status: Mapped[str] = mapped_column(nullable=False, default="completed")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now, onupdate=datetime.now
    )
