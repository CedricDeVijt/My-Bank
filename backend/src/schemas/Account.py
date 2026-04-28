import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(pattern="^(checking|savings)$")
    currency: str = Field(min_length=3, max_length=3)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: uuid.UUID
    account_number: str
    iban: str
    type: str
    currency: str
    balance_cents: int
    status: str
    created_at: date


class AccountListResponse(BaseModel):
    accounts: list[AccountResponse]
