import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TransactionCreateRequest(BaseModel):
    """Request schema for creating a transaction"""

    from_account_id: uuid.UUID = Field(description="ID of the account to transfer from")
    to_account_id: uuid.UUID = Field(description="ID of the account to transfer to")
    amount_cents: int = Field(gt=0, description="Amount in cents (must be positive)")

    @field_validator("from_account_id", "to_account_id")
    @classmethod
    def validate_uuids(cls, v):
        if not v:
            raise ValueError("Account ID cannot be empty")
        return v

    @field_validator("from_account_id")
    @classmethod
    def validate_different_accounts(cls, v, info):
        if "to_account_id" in info.data and v == info.data["to_account_id"]:
            raise ValueError("Cannot transfer to the same account")
        return v


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
