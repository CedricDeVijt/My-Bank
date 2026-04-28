import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base
from src.db.models import User


class Account(Base):
    __tablename__ = "account"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    iban: Mapped[str] = mapped_column(String(34), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    account_holder_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    account_holder: Mapped["User"] = relationship("User", back_populates="accounts")
