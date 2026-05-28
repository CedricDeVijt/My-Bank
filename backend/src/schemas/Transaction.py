import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class TransactionCreateRequest(BaseModel):
    """Request schema for creating a transaction"""

    from_iban: str = Field(description="IBAN of the account to transfer from")
    to_iban: str = Field(description="IBAN of the account to transfer to")
    amount_cents: int = Field(gt=0, description="Amount in cents (must be positive)")

    @field_validator("from_iban", "to_iban", mode="before")
    @classmethod
    def normalize_iban(cls, v: object) -> object:
        if not isinstance(v, str):
            return v

        normalized = v.replace(" ", "").upper()
        if not normalized:
            raise ValueError("IBAN cannot be empty")
        return normalized

    @model_validator(mode="after")
    def validate_different_accounts(self) -> "TransactionCreateRequest":
        if self.from_iban == self.to_iban:
            raise ValueError("Cannot transfer to the same account")
        return self


class TransactionResponse(BaseModel):
    """Response schema for a transaction"""

    id: uuid.UUID
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount_cents: int
    currency: str
    status: str
    failure_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    """Response schema for listing transactions"""

    id: uuid.UUID
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount_cents: int
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
