import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base

if TYPE_CHECKING:
    from src.db.models.Account import Account


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    accounts: Mapped[list["Account"]] = relationship(
        "Account", back_populates="account_holder"
    )
